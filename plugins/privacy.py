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

from telethon import events, functions
from utils.logger import get_logger
from config.config import Config
import time

logger = get_logger("PrivacyPlugin")

# Anti-Flood state
FLOOD_DATA = {} # {user_id: [timestamp1, timestamp2, ...]}
ANTIFLOOD_ENABLED = True
MAX_MSGS = 5
TIME_WINDOW = 10 # seconds
MAX_CACHE_SIZE = 1000 # Memory protection

def setup(ether, db, owner_id):

    # 1. Auto-Read Feature
    @ether.on(events.NewMessage(incoming=True))
    async def auto_read_handler(event):
        if not event.is_private:
            return
            
        if event.sender_id == owner_id:
            return
            
        try:
            await event.mark_read()
        except Exception as e:
            logger.error(f"Auto-read error: {e}")

    # 2. Anti-Flood System
    @ether.on(events.NewMessage(incoming=True))
    async def anti_flood_handler(event):
        global ANTIFLOOD_ENABLED
        if not ANTIFLOOD_ENABLED or not event.is_private:
            return

        user_id = event.sender_id
        if user_id == owner_id:
            return

        now = time.time()
        if user_id not in FLOOD_DATA:
            # Memory Protection: If cache is too big, reset to avoid memory leak
            if len(FLOOD_DATA) > MAX_CACHE_SIZE:
                FLOOD_DATA.clear()
            FLOOD_DATA[user_id] = []

        # Filter out old timestamps
        FLOOD_DATA[user_id] = [t for t in FLOOD_DATA[user_id] if now - t < TIME_WINDOW]
        FLOOD_DATA[user_id].append(now)

        if len(FLOOD_DATA[user_id]) > MAX_MSGS:
            logger.warning(f"Blocking user {user_id} due to flooding.")
            try:
                await ether(functions.contacts.BlockRequest(id=user_id))
                await event.reply("<blockquote>🚫 <b>Flood Detected!</b>\n\nYou have been blocked for spamming.</blockquote>")
                del FLOOD_DATA[user_id]
            except Exception as e:
                logger.error(f"Failed to block flooder: {e}")

    # 3. Privacy Commands
    @ether.on(events.NewMessage(pattern=r"^\.autoread (on|off)$", outgoing=True))
    async def toggle_autoread(event):
        if event.sender_id != owner_id:
            return
        cmd = event.pattern_match.group(1).lower()
        status = "ENABLED" if cmd == "on" else "DISABLED"
        await event.edit(f"<blockquote>👁️ <b>Auto-Read:</b> {status}</blockquote>")

    @ether.on(events.NewMessage(pattern=r"^\.antiflood (on|off)$", outgoing=True))
    async def toggle_antiflood(event):
        global ANTIFLOOD_ENABLED
        if event.sender_id != owner_id:
            return
        cmd = event.pattern_match.group(1).lower()
        ANTIFLOOD_ENABLED = (cmd == "on")
        status = "ENABLED" if ANTIFLOOD_ENABLED else "DISABLED"
        await event.edit(f"<blockquote>🛡️ <b>Anti-Flood:</b> {status}</blockquote>")

    logger.info("Privacy plugin loaded (Auto-read & Anti-flood active)")
