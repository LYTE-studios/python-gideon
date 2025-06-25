import discord
import asyncio
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
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        if message.channel.id != self.target_channel_id:
            return  # Ignore messages from other channels

        # Only respond if bot is mentioned in the message
        if self.user not in message.mentions:
            return

        # Remove the mention (could be at start, end, or middle)
        content = message.content
        mention_str = f"<@{self.user.id}>"
        content = content.replace(mention_str, "").strip()
        logger.info(f"Bot was mentioned. Extracted message: '{content}'")

        if not content:
            # Don't respond to empty messages/mentions
            return

        # Call OpenAI to generate a reply
        response = await self.openai_client.ask_chatgpt(content)
        await message.channel.send(response)

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

    client = GideonBot(
        channel_id=config.get_channel_id(),
        openai_client=openai_client,
        intents=intents
    )
    client.run(config.get_token())

if __name__ == "__main__":
    main()