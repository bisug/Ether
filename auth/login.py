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

from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError
)

from core.user_client import EtherUserClient
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherAuth")


class EtherAuthManager:
    def __init__(self):
        self.client_wrapper = EtherUserClient()
        self.client = self.client_wrapper.get_client()

        self.phone = None
        self.phone_code_hash = None

    async def connect(self):
        await self.client_wrapper.connect()

    async def send_otp(self, phone: str):
        try:
            await self.connect()

            self.phone = phone

            result = await self.client.send_code_request(phone)
            self.phone_code_hash = result.phone_code_hash

            logger.info(f"📩 OTP sent to {phone}")
            return "OTP_SENT"

        except FloodWaitError as e:
            logger.warning(f"⏳ FloodWait: {e.seconds}s")
            return f"FLOOD_WAIT_{e.seconds}"

        except Exception as e:
            logger.error(f"❌ OTP Error: {e}")
            return "ERROR"

    async def verify_otp(self, code: str):
        try:
            await self.connect()

            await self.client.sign_in(
                phone=self.phone,
                code=code,
                phone_code_hash=self.phone_code_hash
            )

            logger.info("✅ Ether login successful")
            return "SUCCESS"

        except SessionPasswordNeededError:
            logger.info("🔐 2FA required")
            return "2FA_REQUIRED"

        except PhoneCodeInvalidError:
            return "INVALID_CODE"

        except PhoneCodeExpiredError:
            return "CODE_EXPIRED"

        except Exception as e:
            logger.error(f"❌ Verify OTP Error: {e}")
            return "ERROR"

    async def verify_2fa(self, password: str):
        try:
            await self.connect()

            await self.client.sign_in(password=password)

            logger.info("✅ 2FA verification successful")
            return "SUCCESS"

        except Exception as e:
            logger.error(f"❌ 2FA Error: {e}")
            return "ERROR"

    async def cancel(self):
        logger.info("❌ Ether login cancelled")

    async def finish(self):
        logger.info("🔐 Ether login completed")