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

from telethon import events, functions, Button
from utils.logger import get_logger
from config.config import Config
from core.bot import send_log
from services.dm_service import DMService
from services.dm_shield_service import DMShieldService
import time
import asyncio

logger = get_logger("PrivacyPlugin")

# Anti-Flood Configuration
ANTIFLOOD_ENABLED = True
MAX_MSGS = 5
TIME_WINDOW = 10 # seconds

def setup(ether, db, owner_id):

    dm_service = DMService(db)
    shield_service = DMShieldService(db)

    # 1. Auto-Read Feature
    @ether.on(events.NewMessage(incoming=True))
    async def auto_read_handler(event):
        if not event.is_private or not Config.AUTO_READ:
            return
            
        if event.sender_id == owner_id:
            return
            
        try:
            await event.mark_read()
        except Exception as e:
            logger.error(f"Auto-read error: {e}")

    # 2. Advanced Anti-Spam System
    @ether.on(events.NewMessage(incoming=True))
    async def anti_spam_handler(event):
        global ANTIFLOOD_ENABLED
        if not event.is_private:
            return

        user_id = event.sender_id
        if user_id == owner_id:
            return

        # Check Whitelist
        user_data = await dm_service.get_user(user_id)
        if user_data and user_data.get("allowed"):
            return

        now = time.time()
        
        # --- PART A: Flood Detection ---
        if ANTIFLOOD_ENABLED:
            is_flooding = await dm_service.check_flood(user_id, TIME_WINDOW, MAX_MSGS)
            if is_flooding:
                logger.warning(f"Flood detected for {user_id}. Issuing warning.")
                try:
                    warns = await dm_service.increment_warn(user_id)
                    max_warns = await dm_service.get_max_warns(user_id, owner_id)

                    if warns >= max_warns:
                        await ether(functions.contacts.BlockRequest(id=user_id))
                        await dm_service.temp_block_user(user_id, Config.TEMP_BAN_DURATION)
                        await event.reply(f"<blockquote><b>Final Warning!</b>\n\nYou have been temporarily blocked for {Config.TEMP_BAN_DURATION // 3600} hours after {warns} flood violations.</blockquote>")
                        
                        # LOG TO BOT
                        user = await event.get_sender()
                        name = f"@{user.username}" if user.username else user.first_name
                        log_text = (
                            "<b>SECURITY ALERT: Flood Limit Reached</b>\n\n"
                            f"<b>User:</b> {name} (<code>{user_id}</code>)\n"
                            f"<b>Reason:</b> Repeated flooding ({warns}/{max_warns})\n"
                            f"<b>Action:</b> Temporary Ban ({Config.TEMP_BAN_DURATION // 3600}h)"
                        )
                        await send_log(f"<blockquote>{log_text}</blockquote>", buttons=[[Button.url("View Profile", f"tg://user?id={user_id}")]])
                    else:
                        await event.reply(f"<blockquote><b>SYSTEM WARNING: Flood {warns}/{max_warns}</b>\n\nPlease stop spamming or you will be blocked.</blockquote>")
                except Exception as e:
                    logger.error(f"Flood warning error: {e}")
                return

        # --- PART B: Link/Media Shield for Unknown Users ---
        shield_settings = await shield_service.get(user_id)
        
        text = event.message.message or ""
        is_spammy = False
        reason = ""

        if shield_service.has_link(text):
            is_spammy = True
            reason = "Link detected"
        elif shield_service.has_username(text):
            is_spammy = True
            reason = "Username mention"
        elif event.message.media and not (user_data and user_data.get("message_count", 0) > 2):
            is_spammy = True
            reason = "Unauthorized media"

        if is_spammy:
            try:
                warns = await dm_service.increment_warn(user_id)
                max_warns = await dm_service.get_max_warns(user_id, owner_id)
                
                if warns >= max_warns:
                    await ether(functions.contacts.BlockRequest(id=user_id))
                    await dm_service.temp_block_user(user_id, Config.TEMP_BAN_DURATION)
                    await event.delete()
                    
                    # LOG TO BOT
                    user = await event.get_sender()
                    name = f"@{user.username}" if user.username else user.first_name
                    log_text = (
                        "<b>SECURITY ALERT: Spam Shield Triggered</b>\n\n"
                        f"<b>User:</b> {name} (<code>{user_id}</code>)\n"
                        f"<b>Reason:</b> {reason} ({warns}/{max_warns})\n"
                        f"<b>Action:</b> Temporary Ban ({Config.TEMP_BAN_DURATION // 3600}h)"
                    )
                    await send_log(f"<blockquote>{log_text}</blockquote>", buttons=[[Button.url("View Profile", f"tg://user?id={user_id}")]])
                else:
                    await event.delete() # Still delete the spammy message
                    await event.respond(f"<blockquote><b>SYSTEM WARNING: Spam {warns}/{max_warns}</b>\n\n{reason}s are not allowed from unverified users.</blockquote>")
            except Exception as e:
                logger.error(f"Spam shield warning error: {e}")
            return

    # 3. Privacy Commands
    @ether.on(events.NewMessage(pattern=r"^\.autoread\s+(on|off)$", outgoing=True))
    async def toggle_autoread(event):
        if event.sender_id != owner_id:
            return
            
        mode = event.pattern_match.group(1).lower()
        Config.AUTO_READ = (mode == "on")
        
        await event.edit(f"<blockquote><b>Auto-Read:</b> <code>{mode.upper()}</code>\n\nIncoming messages will now be marked as read.</blockquote>")

    @ether.on(events.NewMessage(pattern=r"^\.antiflood\s+(on|off)$", outgoing=True))
    async def toggle_antiflood(event):
        global ANTIFLOOD_ENABLED
        if event.sender_id != owner_id:
            return
        cmd = event.pattern_match.group(1).lower()
        ANTIFLOOD_ENABLED = (cmd == "on")
        status = "ENABLED" if ANTIFLOOD_ENABLED else "DISABLED"
        await event.edit(f"<blockquote><b>Anti-Flood:</b> {status}</blockquote>")

    # 4. Background Unblocker Task
    async def unblock_task():
        """Periodically checks and unblocks users whose temp ban expired."""
        if db is None:
            return
            
        while True:
            try:
                now = time.time()
                # Find users where unblock_at is in the past
                expired_users = db.dm_users.find({"blocked": True, "unblock_at": {"$lte": now, "$ne": None}})
                
                async for user in expired_users:
                    uid = user["user_id"]
                    try:
                        await ether(functions.contacts.UnblockRequest(id=uid))
                        await db.dm_users.update_one({"user_id": uid}, {"$set": {"blocked": False, "unblock_at": None}})
                        logger.info(f"UnblockTask: Automatically unblocked user {uid}")
                        await send_log(f"<blockquote><b>SYSTEM LOG: Auto-Unblock</b>\n\nUser <code>{uid}</code> has been restored after temporary ban.</blockquote>")
                    except Exception as ue:
                        logger.error(f"UnblockTask error for {uid}: {ue}")
                
            except Exception as e:
                logger.error(f"UnblockTask general error: {e}")
            
            await asyncio.sleep(300) # Check every 5 minutes

    from utils.task_helper import safe_run
    safe_run(unblock_task(), name="AutoUnblocker")

    logger.info("Privacy plugin loaded (Anti-flood & Temp-ban active)")
