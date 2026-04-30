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

import re


# ============================================
# DM Shield Service Class
# ============================================

class DMShieldService:
    def __init__(self, db):
        self.db = db
        self.cache = {}

    async def get(self, user_id: int):

        if user_id in self.cache:
            return self.cache[user_id]

        if self.db is not None:
            data = await self.db.dm_shield.find_one({"user_id": user_id})

            if data and "settings" in data:
                self.cache[user_id] = data["settings"]
                return data["settings"]

        default = {
            "enabled": False,
            "link": False,
            "username": False
        }

        self.cache[user_id] = default
        return default

    async def save(self, user_id: int, settings: dict):

        self.cache[user_id] = settings

        if self.db is not None:
            await self.db.dm_shield.update_one(
                {"user_id": user_id},
                {"$set": {"settings": settings}},
                upsert=True
            )

    def has_link(self, text: str) -> bool:
        if not text:
            return False

        text = text.lower()

        patterns = [
            r"https?://",
            r"t\.me/",
            r"telegram\.me/",
            r"tg://",
            r"www\.",
        ]

        return any(re.search(p, text) for p in patterns)

    def has_username(self, text: str) -> bool:
        if not text:
            return False

        text = text.lower()

        patterns = [
            r"@\w+",
            r"@\u200b\w+",  # zero-width bypass
            r"tg://resolve\?domain=",
        ]

        return any(re.search(p, text) for p in patterns)