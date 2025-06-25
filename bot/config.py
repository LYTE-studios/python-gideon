import os
from dotenv import load_dotenv
from bot.logger import setup_logger

logger = setup_logger("Config")

class BotConfig:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = os.getenv("DISCORD_CHANNEL_ID")
        self.validate()

    def validate(self):
        if not self.token:
            logger.error("DISCORD_BOT_TOKEN is missing in .env")
            raise ValueError("DISCORD_BOT_TOKEN is required in the environment")
        if not self.channel_id:
            logger.error("DISCORD_CHANNEL_ID is missing in .env")
            raise ValueError("DISCORD_CHANNEL_ID is required in the environment")
        if not self.channel_id.isdigit():
            logger.error("DISCORD_CHANNEL_ID must be a numeric string")
            raise ValueError("DISCORD_CHANNEL_ID must be a numeric string")

    def get_token(self):
        return self.token

    def get_channel_id(self):
        return int(self.channel_id)