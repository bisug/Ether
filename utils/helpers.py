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
#    - If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    - Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

import asyncio
import re
from typing import Optional


async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


def extract_chat_id(text: str) -> Optional[str]:
    if not text:
        return None
    
    # @username format
    if text.startswith("@"):
        return text[1:]
    
    # t.me/username format
    match = re.search(r"(?:https?://)?t\.me/([a-zA-Z0-9_]{5,})", text)
    if match:
        return match.group(1)
    
    return None


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    return f"{hours}h {minutes}m"


def safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def is_owner(user_id: int, owner_id: int) -> bool:
    return user_id == owner_id