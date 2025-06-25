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
            f"You are Gideon, a helpful assistant in a Discord server. "
            f"Your recognized names and aliases are: {names_str}. "
            "ONLY reply if the message is clearly meant for you—if the author mentions your name, calls for 'assistant', explicitly refers to a bot, or the request is generic/"
            "open to everyone (such as 'does anyone know...'). "
            "If the message is clearly addressed to someone else, such as 'Mathis, ...', DO NOT reply. "
            "If you are unsure, respond exactly and ONLY with 'NO_REPLY'. "
            "Be concise, friendly, and informative. If asked about future features, answer based on known roadmap plans."
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