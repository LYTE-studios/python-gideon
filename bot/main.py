import discord
import asyncio
import re
import json
from datetime import datetime
from bot.config import BotConfig
from bot.logger import setup_logger

logger = setup_logger("DiscordBot")

from bot.github_client import GitHubClient
class GideonBot(discord.Client):
    def __init__(self, channel_id: int, openai_client, config=None, **kwargs):
        super().__init__(**kwargs)
        self.target_channel_id = channel_id
        self.openai_client = openai_client
        self.config = config
        self.github_client = None
        if config is not None:
            from bot.github_client import GitHubClient
            self.github_client = GitHubClient(
                config.get_github_token(), config.get_github_repo()
            )

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user}")
        logger.info(f"Listening in channel ID: {self.target_channel_id}")
        # Permission check logging
        try:
            # Find the configured text channel in all connected guilds
            target_channel = None
            for guild in self.guilds:
                chan = guild.get_channel(self.target_channel_id)
                if chan:
                    target_channel = chan
                    break
            if not target_channel:
                logger.error(f"Target channel ID {self.target_channel_id} not found in any connected guild.")
                return
            needed_perms = {
                "send_messages": target_channel.permissions_for(target_channel.guild.me).send_messages,
                "view_channel": target_channel.permissions_for(target_channel.guild.me).view_channel,
                "manage_events": target_channel.permissions_for(target_channel.guild.me).manage_events,
            }
            for perm, ok in needed_perms.items():
                if not ok:
                    logger.error(f"Missing required permission: {perm} in {target_channel}")
            if not all(needed_perms.values()):
                logger.error("Bot startup: insufficient permissions in the target channel. Some features will not work!")
        except Exception as e:
            logger.error(f"Error checking permissions at startup: {e}")

    async def on_message(self, message):
        # Ignore messages from the bot itself (or other bots)
        if message.author.bot:
            return

        content = message.content.strip()
        logger.info(f"Message in #{message.channel.name}: '{content}'")
        if not content:
            return

        main_channel_id = self.target_channel_id
        in_main_channel = (message.channel.id == main_channel_id)

        # Per-instructions:
        # In non-main channels, only respond if
        #   (A) the bot is mentioned
        #   (B) the message is a reply to the bot's message
        def is_reply_to_bot(msg):
            # Discord implements reply by message reference
            return msg.reference and hasattr(msg.reference, "resolved") and getattr(msg.reference.resolved, "author", None) == self.user

        explicitly_mentioned = self.user in message.mentions
        replying_to_bot = is_reply_to_bot(message)

        if not in_main_channel and not (explicitly_mentioned or replying_to_bot):
            logger.info("Ignoring message: not in main channel, not mentioned, not a reply to me.")
            return

        import re
        import json
        from datetime import datetime

        # Gather bot's possible names/aliases (username, display_name, 'assistant', 'gideon')
        bot_names = [
            str(self.user.name),
            str(self.user.display_name),
            "assistant",
            "gideon"
        ]
        # Gather last 10 recent text messages (for context, oldest first)
        history = []
        async for msg in message.channel.history(limit=10, oldest_first=True):
            if not msg.content:
                continue
            role = "assistant" if msg.author.bot else "user"
            history.append({"role": role, "content": msg.content})

        # Simple code/dev-related query detection
        def is_code_question(msg):
            code_keywords = [
                "python", "java", "js", "typescript", "react", "bug", "debug", "error", "stack trace", "exception",
                "variable", "function", "method", "class", "loop", "array", "dict", "dictionary", "object",
                "API", "database", "sql", "NoSQL", "compil", "build", "deploy", "docker", "test case", "test failed", "pytest", "package", "import",
                "code:", "```", "try:", "def ", "public ", "private ", "const ", "let ", "var "
            ]
            pr_keywords = [
                "pull request", "open a pr", "make a pr", "create a pr", "start a pr", "github pr", "review pr", "merge this", "branch and pr"
            ]
            text = msg.lower()
            if any(pr_kw in text for pr_kw in pr_keywords):
                return "pr"
            if "```" in text:
                return True
            for kw in code_keywords:
                if kw in text:
                    return True
            return False

        channel_name = str(message.channel.name).lower() if hasattr(message.channel, 'name') else ""
        code_check = is_code_question(content)
        # PR requests delegated for future GH integration (stub)
        if code_check == "pr":
            await message.channel.send("👷 PR request detected! This functionality is being implemented and will be available soon.")
            logger.info("Detected PR automation request.")
            return

        persona = "developer" if code_check else "assistant"
        response = await self.openai_client.ask_chatgpt(
            content, bot_names=bot_names, history=history, persona=persona, channel_name=channel_name
        )

        # Remove NO_REPLY logic: LLM must answer everything routed here
        # Previously: if response.strip().upper() == "NO_REPLY": ...

        # typing only if we are actually responding
        async with message.channel.typing():
            # Look for event blocks in response
            sched_match = re.search(r"\[SCHEDULE_EVENT\](.*?)\[/SCHEDULE_EVENT\]", response, re.DOTALL)
            update_match = re.search(r"\[UPDATE_EVENT\](.*?)\[/UPDATE_EVENT\]", response, re.DOTALL)
            cancel_match = re.search(r"\[CANCEL_EVENT\](.*?)\[/CANCEL_EVENT\]", response, re.DOTALL)

            if sched_match:
                block = sched_match.group(1).strip()
                try:
                    event_data = json.loads(block)
                    logger.info(f"Scheduling Discord event: {event_data}")
                    await self.create_discord_event(message, event_data)
                    return
                except Exception as e:
                    error_log = f"Failed to parse or create event: {e}\nBlock:{block}"
                    logger.error(error_log)
                    await message.channel.send(
                        "Sorry, I couldn't schedule that event (invalid details or Discord error).\n"
                        f"```py\n{error_log}\n```"
                    )
                    return
            elif update_match:
                block = update_match.group(1).strip()
                try:
                    event_data = json.loads(block)
                    logger.info(f"Updating Discord event: {event_data}")
                    await self.update_discord_event(message, event_data)
                    return
                except Exception as e:
                    error_log = f"Failed to parse or update event: {e}\nBlock:{block}"
                    logger.error(error_log)
                    await message.channel.send(
                        "Sorry, I couldn't update that event (invalid details or Discord error).\n"
                        f"```py\n{error_log}\n```"
                    )
                    return
            elif cancel_match:
                block = cancel_match.group(1).strip()
                try:
                    event_data = json.loads(block)
                    logger.info(f"Cancelling Discord event: {event_data}")
                    await self.cancel_discord_event(message, event_data)
                    return
                except Exception as e:
                    error_log = f"Failed to parse or cancel event: {e}\nBlock:{block}"
                    logger.error(error_log)
                    await message.channel.send(
                        "Sorry, I couldn't cancel that event (invalid details or Discord error).\n"
                        f"```py\n{error_log}\n```"
                    )
                    return

            # Otherwise, normal response
            await message.channel.send(response)

    async def create_discord_event(self, message, event_data):
        """
        Creates a Discord scheduled event based on parsed event_data.
        """
        guild = message.guild
        if not guild:
            await message.channel.send("Could not create event: not in a server.")
            return
        try:
            start = event_data.get("datetime") or event_data.get("start_time")
            tz = event_data.get("timezone", "Europe/Brussels")
            title = event_data.get("title", "Scheduled Event")
            desc = event_data.get("description", "")
            from datetime import timezone, timedelta
            start_dt = datetime.fromisoformat(start)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)
            if start_dt < now_utc:
                error_log = (
                    f"Scheduled start time is in the past. "
                    f"start_dt={start_dt.isoformat()}, now_utc={now_utc.isoformat()}"
                )
                logger.error(error_log)
                await message.channel.send(
                    "Sorry, the event couldn't be created because the scheduled time is in the past. "
                    "Please use a future date/time!\n"
                    f"```py\n{error_log}\n```"
                )
                return
            # Make event private to the guild/online location
            # Decide event type
            if message.channel.type == discord.ChannelType.voice:
                entity_type = discord.EntityType.voice
                scheduled_event = await guild.create_scheduled_event(
                    name=title[:100],
                    start_time=start_dt,
                    end_time=None,
                    description=desc[:1000] or "No description.",
                    channel=message.channel,
                    privacy_level=discord.PrivacyLevel.guild_only,
                    entity_type=entity_type,
                )
            else:
                entity_type = discord.EntityType.external
                external_end_dt = start_dt + timedelta(hours=1)
                if external_end_dt < now_utc:
                    error_log = (
                        f"Scheduled end time is in the past. "
                        f"external_end_dt={external_end_dt.isoformat()}, now_utc={now_utc.isoformat()}"
                    )
                    logger.error(error_log)
                    await message.channel.send(
                        "Sorry, the event couldn't be created because the end time is in the past. "
                        "Please use a future date/time!\n"
                        f"```py\n{error_log}\n```"
                    )
                    return
                scheduled_event = await guild.create_scheduled_event(
                    name=title[:100],
                    start_time=start_dt,
                    end_time=external_end_dt,
                    description=desc[:1000] or "No description.",
                    privacy_level=discord.PrivacyLevel.guild_only,
                    entity_type=entity_type,
                    location="Discord"
                )
            await message.channel.send(f"✅ Created event **{title}** for {start} ({tz})!")
        except Exception as e:
            error_log = f"Discord event creation failed: {e}"
            logger.error(error_log)
            await message.channel.send(
                "Sorry, something went wrong creating the event in Discord!\n"
                f"```py\n{error_log}\n```"
            )

    async def update_discord_event(self, message, event_data):
        """
        Update a scheduled event based on event_data.
        """
        guild = message.guild
        if not guild:
            await message.channel.send("Could not update event: not in a server.")
            return
        try:
            title = event_data.get("title")
            dt_str = event_data.get("datetime")
            new_fields = event_data.get("fields_to_update", {})
            found_event = await self._find_event(guild, title, dt_str)
            if not found_event:
                await message.channel.send(f"Sorry, couldn't find an event to update for title/datetime: {title} / {dt_str}")
                return
            await found_event.edit(**new_fields)
            await message.channel.send(f"✅ Updated event **{title}**.")
        except Exception as e:
            error_log = f"Event update failed: {e}"
            logger.error(error_log)
            await message.channel.send(
                "Sorry, something went wrong updating the event!\n"
                f"```py\n{error_log}\n```"
            )

    async def cancel_discord_event(self, message, event_data):
        """
        Cancel/delete a scheduled event based on event_data.
        """
        guild = message.guild
        if not guild:
            await message.channel.send("Could not cancel event: not in a server.")
            return
        try:
            title = event_data.get("title")
            dt_str = event_data.get("datetime")
            found_event = await self._find_event(guild, title, dt_str)
            if not found_event:
                await message.channel.send(f"Sorry, couldn't find an event to cancel for title/datetime: {title} / {dt_str}")
                return
            await found_event.delete()
            await message.channel.send(f"🗑️ Cancelled event **{title}**.")
        except Exception as e:
            error_log = f"Event cancel failed: {e}"
            logger.error(error_log)
            await message.channel.send(
                "Sorry, something went wrong canceling the event!\n"
                f"```py\n{error_log}\n```"
            )

    async def _find_event(self, guild, title, dt_str):
        """
        Find the closest matching scheduled event by title and datetime (ISO), fallback to best (fuzzy) match if needed.
        """
        events = await guild.fetch_scheduled_events()
        norm = lambda s: s.lower() if s else ""
        title_norm = norm(title)
        dt_norm = norm(dt_str)
        found_event = None

        # Try exact datetime+title match
        for ev in events:
            if dt_str:
                try:
                    iso_cmp = ev.scheduled_start_time.isoformat().replace("+00:00", "Z")
                    # Allow match with or without ms, Z or not
                    if iso_cmp.startswith(dt_str.replace("+00:00", "Z")) or dt_str.startswith(iso_cmp):
                        if title and title_norm in norm(ev.name):
                            return ev
                        if not title:
                            return ev
                except Exception:
                    continue
        # If no datetime, try title-based fuzzy match (most recent first)
        if title:
            for ev in sorted(events, key=lambda e: e.scheduled_start_time, reverse=True):
                if title_norm in norm(ev.name) or title_norm in norm(ev.description):
                    return ev
        # If neither found, but only one event exists, assume that's what user means
        if len(events) == 1:
            return events[0]
        # Fallback: return most recent if nothing else
        if events:
            return sorted(events, key=lambda e: e.scheduled_start_time, reverse=True)[0]
        return None

from bot.openai_client import OpenAIClient

def main():
    try:
        config = BotConfig()
    except ValueError as e:
        logger.error(f"Config error: {e}")
        exit(1)

    openai_client = OpenAIClient(api_key=config.get_openai_key())
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True  # Needed to reliably access message.content

    client = GideonBot(
        channel_id=config.get_channel_id(),
        openai_client=openai_client,
        config=config,
        intents=intents
    )
    client.run(config.get_token())

if __name__ == "__main__":
    main()