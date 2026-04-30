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

from telethon import events
from utils.logger import get_logger
from services.dm_shield_service import DMShieldService
from config.config import Config

logger = get_logger("DMShield")


def setup(ether, db, owner_id):

    shield = DMShieldService(db)
# ============================================
# Dm filter
# ============================================
    @ether.on(events.NewMessage(incoming=True))
    async def dm_filter(event):
    
        if not event.is_private:
            return
    
        if event.sender_id == owner_id:
            return
    
        settings = await shield.get(owner_id)
    
        # 🔥 DEBUG (remove later if needed)
        logger.info(f"DM CHECK FROM: {event.sender_id}")
        logger.info(f"SETTINGS: {settings}")
    
        if not settings.get("enabled"):
            return
    
        text = event.raw_text or ""
    
        block = False
    
        if settings.get("link") and shield.has_link(text):
            block = True
    
        if settings.get("username") and shield.has_username(text):
            block = True
    
        if block:
            try:
                await event.delete()
                logger.info(f"Deleted DM from {event.sender_id}")
            except Exception as e:
                logger.error(f"DM delete failed: {e}")

# ============================================
# Shield Allow
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shield allow$", outgoing=True))
    async def shield_allow(event):
    
        if event.sender_id != owner_id:
            return
    
        if not event.is_reply:
            await event.reply("❌ Reply to a user DM to allow them.")
            return
    
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    
        settings = await shield.get(owner_id)
    
        allowed = settings.get("allowed", [])
    
        if user_id not in allowed:
            allowed.append(user_id)
            settings["allowed"] = allowed
            await shield.save(owner_id, settings)
    
        await event.reply(f"✅ User {user_id} is now ALLOWED in DM Shield")
    
# ============================================
# Shield Disallow
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shield disallow$", outgoing=True))
    async def shield_disallow(event):
    
        if event.sender_id != owner_id:
            return
    
        if not event.is_reply:
            await event.reply("❌ Reply to a user DM to disallow them.")
            return
    
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    
        settings = await shield.get(owner_id)
    
        allowed = settings.get("allowed", [])
    
        if user_id in allowed:
            allowed.remove(user_id)
            settings["allowed"] = allowed
            await shield.save(owner_id, settings)
    
        await event.reply(f"❌ User {user_id} is now REMOVED from allowed list")
    
    
# ============================================
# Shield Help
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield$", outgoing=True))
    async def shield_help(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)

        msg = (
            "🛡️ <b>DM Shield System</b>\n\n"
            "<b>Status:</b>\n"
            f"Enabled: {'✅' if settings.get('enabled') else '❌'}\n"
            f"Links: {'✅' if settings.get('link') else '❌'}\n"
            f"Usernames: {'✅' if settings.get('username') else '❌'}\n\n"
            "<b>Commands:</b>\n"
            "<code>.shield on</code>\n"
            "<code>.shield off</code>\n"
            "<code>.shield link</code>\n"
            "<code>.shield user</code>\n"
            "<code>.shield status</code>"
        )

        await event.reply(msg, parse_mode="html")

# ============================================
# Shield On
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield on$", outgoing=True))
    async def shield_on(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["enabled"] = True
        await shield.save(owner_id, settings)

        await event.reply("🛡️ Shield ENABLED")


# ============================================
# Shield Off
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield off$", outgoing=True))
    async def shield_off(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["enabled"] = False
        await shield.save(owner_id, settings)

        await event.reply("❌ Shield DISABLED")


# ============================================
# Shield Link
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield link$", outgoing=True))
    async def shield_link(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["link"] = not settings.get("link", False)
        await shield.save(owner_id, settings)

        await event.reply(
            f"🔗 Links {'ENABLED' if settings['link'] else 'DISABLED'}"
        )


# ============================================
# Shield User
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield user$", outgoing=True))
    async def shield_user(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["username"] = not settings.get("username", False)
        await shield.save(owner_id, settings)

        await event.reply(
            f"👤 Usernames {'ENABLED' if settings['username'] else 'DISABLED'}"
        )


# ============================================
# Shield Status
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield status$", outgoing=True))
    async def shield_status(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)

        await event.reply(
            "🛡️ <b>Shield Status</b>\n\n"
            f"Enabled: {'✅' if settings.get('enabled') else '❌'}\n"
            f"Links: {'✅' if settings.get('link') else '❌'}\n"
            f"Usernames: {'✅' if settings.get('username') else '❌'}",
            parse_mode="html"
        )