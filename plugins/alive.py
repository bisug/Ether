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

from telethon import events, Button
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherAlive")


def setup(ether, db, owner_id):

    from core.buttons import ether_bot
    bot_username = Config.BOT_USERNAME or ""

    ALIVE_IMAGE = Config.START_IMG_URL

    @ether.on(events.NewMessage(pattern=r"^\.alive$", outgoing=True))
    async def alive_handler(event):

        if event.sender_id != owner_id:
            return

        # Use dynamically fetched username if available
        target_username = bot_username
        if ether_bot.me and ether_bot.me.username:
            target_username = ether_bot.me.username

        if not target_username:
            await event.reply("BOT_USERNAME not set and bot not initialized.")
            return

        try:
            await event.delete()

            results = await ether.inline_query(
                target_username,
                "alive"
            )

            if results:
                await results[0].click(event.chat_id)
            else:
                await event.respond("Inline failed: no result returned.")

        except Exception as e:
            logger.error(f"Alive error: {e}")
            await event.respond("Alive failed.")