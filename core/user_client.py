# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/Ether_Update
#
#  License:       Open Source (Keep Credits)
#
#  IMPORTANT:
#    • If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    • Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

from telethon import TelegramClient
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherUserClient")


class EtherUserClient:
    
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# ============================================
# Client Management
# ============================================

    @property
    def client(self) -> TelegramClient:
        if self._client is None:
            self._client = TelegramClient(
                Config.SESSION_NAME,
                Config.API_ID,
                Config.API_HASH
            )
        return self._client

    async def connect(self) -> bool:
        try:
            await self.client.connect()
            logger.info("Telegram client connected")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self) -> None:
        try:
            if self._client and self._client.is_connected():
                await self._client.disconnect()
                logger.info("Telegram client disconnected")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

    async def is_authorized(self) -> bool:
        try:
            return await self.client.is_user_authorized()
        except Exception as e:
            logger.error(f"Auth check failed: {e}")
            return False

    def get_client(self) -> TelegramClient:
        return self.client