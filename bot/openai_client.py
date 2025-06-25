import aiohttp
import asyncio
from bot.logger import setup_logger

logger = setup_logger("OpenAI")

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def ask_chatgpt(self, message: str, bot_names=None) -> str:
        """
        message: The discord message string to analyze/respond.
        bot_names: A list of recognized names/aliases for the bot (str or list)
        """
        if bot_names is None:
            bot_names = []
        # allow both str and list
        if isinstance(bot_names, str):
            bot_names = [bot_names]
        names_str = ", ".join(f'"{n}"' for n in bot_names if n)

        sys_prompt = (
            f"You are Gideon, a Discord bot assistant. "
            f"Your recognized names and aliases are: {names_str}. "
            "You are very careful not to respond to messages not intended for you. "
            "HOWEVER: If the user's message refers to you by name, uses 'assistant' or your alias, mentions or tags you, or otherwise asks your opinion or for help, ALWAYS respond. "
            "Do NOT refuse to answer simply because someone else's name is mentioned—if the message is for you, reply helpfully, even if other members are referenced. "
            "Conversely, if it is entirely for someone else and not you at all, reply with 'NO_REPLY'. "
            "When in doubt, but your name/alias appears or you're asked a question, err on the side of answering. "
            "If the user is asking to schedule/plan a meeting, event, or reminder, respond ONLY in this strict format—replace fields, do NOT add any commentary or explanation, do NOT answer outside this format:"
            "\n[SCHEDULE_EVENT]\n"
            "{\n  \"title\": \"...\","
            "\n  \"description\": \"...\","
            "\n  \"participants\": [\"...\"],"
            "\n  \"datetime\": \"...\","
            "\n  \"timezone\": \"...\""
            "\n}\n[/SCHEDULE_EVENT]\n"
            "Do NOT explain the format—ONLY use the event block or 'NO_REPLY'."
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
                {"role": "system", "content": sys_prompt},
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