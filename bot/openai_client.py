import aiohttp
import asyncio
from bot.logger import setup_logger

logger = setup_logger("OpenAI")

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def ask_chatgpt(self, message: str, bot_names=None, history=None) -> str:
        """
        message: The discord message string to analyze/respond.
        bot_names: A list of recognized names/aliases for the bot (str or list)
        history: A list of {"role": "user"|"assistant", "content": str} dicts representing recent chat history.
        """
        if bot_names is None:
            bot_names = []
        if history is None:
            history = []
        # allow both str and list
        if isinstance(bot_names, str):
            bot_names = [bot_names]
        names_str = ", ".join(f'"{n}"' for n in bot_names if n)

        # Add current date/time context in prompt
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        now_str = now.isoformat()
        tz_str = now.tzname() or str(now.utcoffset())
        sys_prompt = (
            f"It is now {now_str} ({tz_str}). "
            f"You are Gideon, a Discord bot assistant. "
            f"Your recognized names and aliases are: {names_str}. "
            "You are extremely strict and careful NOT to respond to any messages unless you are directly, explicitly addressed. "
            "You must reply if the message clearly, specifically addresses you: "
            "by your Discord username, display name, a direct @mention/tag, using one of your aliases or 'assistant', "
            "or if the message starts directly with one of these names and is structured as a request for your help (e.g. 'Gideon, can you...', 'assistant please schedule...'). "
            "If someone else is mentioned but you are clearly and directly called on, you SHOULD reply. "
            "If you are referenced by a mention tag (like <@your_id> or <@&your_role_id>), you MUST reply. "
            "If the user's message includes your name, nickname, alias, or a Discord mention ANYWHERE in the message, and is a valid sentence, greeting, or question, you MUST ALWAYS reply. "
            "This includes lines like 'How are you doing Gideon?', 'Hey assistant!', 'Are you there, Gideon?', '<@your_id> what's up?'. Respond every time you are referenced by name or tag. "
            "If the recent conversation context suggests you should reply (such as a follow-up or clarification request after a prior answer), you MAY reply. "
            "But if you are not addressed at all and there is no conversational cue, reply ONLY with 'NO_REPLY'. "
            "Do not respond to conversations between other users, unless specifically called by name or mentioned."
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
            "Do NOT explain the format—ONLY use one of the event blocks or 'NO_REPLY'."
            "Otherwise, reply as normal if and ONLY IF the user's message is clearly for you. Be brief, direct, and only respond when 100% confident."
            "Be concise. If asked about future features, answer based on known roadmap plans."
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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        logger.error(f"OpenAI API returned {resp.status}: {await resp.text()}")
                        return "Sorry, I couldn't generate an answer right now (OpenAI error)."
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return content.strip()
        except Exception as e:
            logger.error(f"OpenAI API failure: {e}")
            return "Sorry, something went wrong with my assistant brain (OpenAI error)."