# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/EtherUserbot
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

import os
from core.user_client import EtherUserClient
from config.config import Config


def session_exists() -> bool:
    return os.path.exists(f"{Config.SESSION_NAME}.session")


async def is_session_authorized() -> bool:
    client_wrapper = EtherUserClient()

    await client_wrapper.connect()

    try:
        return await client_wrapper.is_authorized() is True

    except Exception:
        return False