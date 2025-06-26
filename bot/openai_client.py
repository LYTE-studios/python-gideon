import aiohttp
import asyncio
from bot.logger import setup_logger

logger = setup_logger("OpenAI")

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def ask_chatgpt(self, message: str, bot_names=None, history=None, persona="assistant", channel_name="") -> str:
        """
        message: The discord message string to analyze/respond.
        bot_names: A list of recognized names/aliases for the bot (str or list)
        history: A list of {"role": "user"|"assistant", "content": str} dicts representing recent chat history.
        persona: "assistant" (default) or "developer" for code/software answers.
        channel_name: The name of the Discord channel where this message was posted, for context.
        """
        if bot_names is None:
            bot_names = []
        if history is None:
            history = []
        if channel_name is None:
            channel_name = ""
        # allow both str and list
        if isinstance(bot_names, str):
            bot_names = [bot_names]
        names_str = ", ".join(f'"{n}"' for n in bot_names if n)

        # Add current date/time context in prompt
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        now_str = now.isoformat()
        tz_str = now.tzname() or str(now.utcoffset())

        dev_keywords = ["dev", "code", "engineering", "developer", "backend", "frontend", "python", "java", "typescript", "review"]
        is_dev_channel = any(k in channel_name for k in dev_keywords)

        if persona == "developer":
            sys_prompt = (
                f"It is now {now_str} ({tz_str}). "
                f"This message was sent in the Discord channel '{channel_name}'. "
                "You are Gideon, a senior software engineer developer on Discord. "
                "You ONLY answer technical questions about programming, software, code, design, bugs, code review, or engineering topics. "
                "If the user asks for help with code, architecture, dev tools, pull requests, or anything technical, reply in detail as a helpful, concise expert. "
                "You may use Markdown code blocks and explain like a top Stack Overflow answer. "
                f"If the current channel name contains development-related keywords (like dev, code, engineering), you SHOULD always answer technical questions even if not explicitly tagged. "
                "If the channel is for casual chat (like 'coffee-machine', 'random', 'social'), only answer if you are directly addressed, mentioned, or tagged in a technical question—but still err on the side of helping if clearly called on. "
                "If the question is not technical, or is about events/scheduling/personal help, reply ONLY (exactly) with 'NO_REPLY'."
            )
        else:
            sys_prompt = (
                f"It is now {now_str} ({tz_str}). "
                f"This message was sent in the Discord channel '{channel_name}'. "
                f"You are Gideon, a Discord bot assistant. "
                f"Your recognized names and aliases are: {names_str}. "
                "If the user asks a factual, calculation, or informational question (e.g., 'what's 3+2', 'what year is it?', 'how do I X?'), always answer directly and informatively—do not reply with generic help offers. "
                "If the user is asking to schedule/plan a meeting, event, or reminder, respond ONLY in this strict format—replace fields, do NOT add any commentary or explanation, do NOT answer outside this format:"
                "\n[SCHEDULE_EVENT]\n"
                "{\n  \"title\": \"...\","
                "\n  \"description\": \"...\","
                "\n  \"participants\": [\"...\"],"
                "\n  \"datetime\": \"...\","
                "\n  \"timezone\": \"...\""
                "\n}\n[/SCHEDULE_EVENT]\n"
                "If the user is asking you to update or edit an existing event, respond ONLY in this format (do not add extra text or chat):"
                "\n[UPDATE_EVENT]\n"
                "{\n  \"title\": \"...\","
                "\n  \"datetime\": \"...\","
                "\n  \"fields_to_update\": { \"location\": \"...\", \"description\": \"...\", ... }"
                "\n}\n[/UPDATE_EVENT]\n"
                "If the user is asking you to cancel/delete an event, respond ONLY in this format (do not add extra text or chat):"
                "\n[CANCEL_EVENT]\n"
                "{\n  \"title\": \"...\","
                "\n  \"datetime\": \"...\""
                "\n}\n[/CANCEL_EVENT]\n"
                "IMPORTANT: The \"datetime\" field MUST ALWAYS be a valid ISO 8601 string (e.g., 2025-06-25T20:00:00), NOT natural language. DO NOT use 'tonight', 'tomorrow', etc.—always convert to a full ISO timestamp. "
                "If the user uses natural language (such as 'tonight', 'tomorrow at 8pm', etc), ALWAYS interpret this as Europe/Brussels time unless they specify a different timezone. "
                "If the user requests a date/time that is in the past, explain that scheduling past events is not possible and ask them to give a valid time in the future. "
                "If you do not have enough context to identify the event, ask the user for clarification."
                "Do NOT explain the format—ONLY use one of the event blocks."
                "Be brief, direct, and concise. If asked about future features, answer based on known roadmap plans."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": sys_prompt}
            ] + history + [
                {"role": "user", "content": message}
            ],
            "max_tokens": 256,
            "temperature": 0.7
        }



async def ask_select_event_to_cancel(self, original_prompt: str, events: list) -> str:
        """
        Given user cancel prompt and a list of events, ask LLM which event to cancel.
        events: list of dicts with id, title, description, start_time (iso)
        Returns: the event id string (or csv if more than one to cancel)
        """
        sys_prompt = (
            "You are an expert Discord scheduling assistant. "
            "The user wants to cancel an event, but it's ambiguous. "
            "Below is a list of scheduled events in the server and the user's command."
            "Please choose the ONE correct event id (or a CSV list if cancelling multiple), and output ONLY the id(s) in your response, nothing else."
            "If you are unsure, pick the closest likely match. If no event fits, reply with 'NONE'."
            "\nEvents:\n"
        )
        events_str = "\n".join(
            f"  - id={ev['id']} title={ev['name']} time={ev['start_time']} desc={ev.get('description','')}" for ev in events
        )
        full_prompt = (
            sys_prompt
            + events_str
            + "\nUser command: "
            + original_prompt
            + "\nWhich event id(s) should be cancelled (csv or single id, or NONE)?"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": full_prompt}
            ],
            "max_tokens": 32,
            "temperature": 0.1
        }
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        logger.error(f"OpenAI event select to cancel failure: {resp.status}: {await resp.text()}")
                        return ""
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return content.strip()
        except Exception as e:
            logger.error(f"OpenAI event select to cancel failure: {e}")
            return ""


async def ask_router_persona(self, message: str) -> str:
        """
        Calls a dedicated router system prompt to select from predefined personas/services.
        Returns the selected persona string, e.g. 'DEVELOPER', 'EVENT', 'ASSISTANT'.
        """
        system_prompt = (
            "You are a routing assistant. You will be given a user's message. "
            "You MUST select and output EXACTLY ONE of these personalities or services "
            "(no natural language):\n\n"
            "DEVELOPER: for any programming, code, bug, review, code generation, software/dev questions.\n"
            "EVENT: for anything related to meeting scheduling, event planning, reminders, times, or Discord event management.\n"
            "ASSISTANT: for all other requests—productivity, general knowledge, fun, or when the request fits none of the above.\n\n"
            "Return only the one service/personality name (no extra text, no chat, uppercase, no explanations)."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "max_tokens": 12,
            "temperature": 0.0
        }
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers={
                    "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"
                }, timeout=30) as resp:
                    if resp.status != 200:
                        logger.error(f"Router LLM returned {resp.status}: {await resp.text()}")
                        return ""
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return content.strip().upper()
        except Exception as e:
            logger.error(f"Router LLM persona select failure: {e}")
            return ""