import discord
import asyncio
import re
import json
from datetime import datetime
from bot.config import BotConfig
from bot.logger import setup_logger

logger = setup_logger("DiscordBot")

class GideonBot(discord.Client):
    def __init__(self, channel_id: int, openai_client, **kwargs):
        super().__init__(**kwargs)
        self.target_channel_id = channel_id
        self.openai_client = openai_client

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user}")
        logger.info(f"Listening in channel ID: {self.target_channel_id}")

    async def on_message(self, message):
        # Ignore messages from the bot itself (or other bots)
        if message.author.bot:
            return

        content = message.content.strip()
        logger.info(f"Message in #{message.channel.name}: '{content}'")
        if not content:
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
        response = await self.openai_client.ask_chatgpt(content, bot_names=bot_names)
        if response.strip().upper() == "NO_REPLY":
            logger.info("Assistant chose not to reply to this message.")
            return

        # typing only if we are actually responding
        async with message.channel.typing():
            # Look for [SCHEDULE_EVENT] block
            sched_match = re.search(r"\[SCHEDULE_EVENT\](.*?)\[/SCHEDULE_EVENT\]", response, re.DOTALL)
            if sched_match:
                block = sched_match.group(1).strip()
                try:
                    event_data = json.loads(block)
                    logger.info(f"Scheduling Discord event: {event_data}")
                    # Try to schedule event; use a helper for clarity
                    await self.create_discord_event(message, event_data)
                    return
                except Exception as e:
                    logger.error(f"Failed to parse or create event: {e}\nBlock:{block}")
                    await message.channel.send("Sorry, I couldn't schedule that event (invalid details or Discord error).")
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
            # For now, use text channel as location
            start_dt = datetime.fromisoformat(start)
            # Make event private to the guild/online location
            scheduled_event = await guild.create_scheduled_event(
                name=title[:100],
                start_time=start_dt,
                end_time=None,
                description=desc[:1000] or "No description.",
                channel=message.channel,
                privacy_level=discord.PrivacyLevel.guild_only,
                entity_type=discord.EntityType.voice if message.channel.type==discord.ChannelType.voice else discord.EntityType.external,
                location="Discord" if message.channel.type!=discord.ChannelType.voice else None
            )
            await message.channel.send(f"✅ Created event **{title}** for {start} ({tz})!")
        except Exception as e:
            logger.error(f"Discord event creation failed: {e}")
            await message.channel.send("Sorry, something went wrong creating the event in Discord!")

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
        intents=intents
    )
    client.run(config.get_token())

if __name__ == "__main__":
    main()