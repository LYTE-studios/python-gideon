import aiohttp
import asyncio
from bot.logger import setup_logger

logger = setup_logger("OpenAI")

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def ask_chatgpt(self, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": (
                    "You are Gideon, a helpful assistant in a Discord server. "
                    "Be concise, friendly, and informative. If asked about future features, answer based on known roadmap plans."
                )},
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