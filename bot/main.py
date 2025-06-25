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
        # Ignore messages from the bot itself (or other bots)
        if message.author.bot:
            return

        content = message.content.strip()
        logger.info(f"Message in #{message.channel.name}: '{content}'")
        if not content:
            return

        async with message.channel.typing():
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
    intents.message_content = True  # Needed to reliably access message.content

    client = GideonBot(
        channel_id=config.get_channel_id(),
        openai_client=openai_client,
        intents=intents
    )
    client.run(config.get_token())

if __name__ == "__main__":
    main()