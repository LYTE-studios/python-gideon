import discord
import asyncio
from bot.config import BotConfig
from bot.logger import setup_logger

logger = setup_logger("DiscordBot")

class GideonBot(discord.Client):
    def __init__(self, channel_id: int, **kwargs):
        super().__init__(**kwargs)
        self.target_channel_id = channel_id

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user}")
        logger.info(f"Listening in channel ID: {self.target_channel_id}")

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        if message.channel.id != self.target_channel_id:
            return  # Ignore messages from other channels

        logger.info(f"Received message in target channel: {message.content}")

        # For now, just acknowledge receipt for testing
        await message.channel.send(f"👋 Hi! I see your message: '{message.content}'")

def main():
    try:
        config = BotConfig()
    except ValueError as e:
        logger.error(f"Config error: {e}")
        exit(1)

    intents = discord.Intents.default()
    intents.messages = True
    client = GideonBot(channel_id=config.get_channel_id(), intents=intents)
    client.run(config.get_token())

if __name__ == "__main__":
    main()