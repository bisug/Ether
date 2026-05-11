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
# =============================================================================

from telethon import events
from utils.logger import get_logger
import asyncio
import time
import re

logger = get_logger("EtherAutoReply")

# In-memory triggers
# Structure: { "trigger": { "text": "...", "msg_id": 123, "chat_id": 456 } }
REPLY_DATA = {}

# Rate Limiting: { user_id: last_trigger_time }
COOLDOWN_DATA = {}
COOLDOWN_TIME = 5  # Seconds between replies per user

def setup(ether, db, owner_id):
    
    async def load_triggers():
        if db is not None:
            triggers = db.autoreplies.find({})
            async for t in triggers:
                REPLY_DATA[t["trigger"].lower()] = {
                    "text": t.get("text"),
                    "msg_id": t.get("msg_id"),
                    "chat_id": t.get("chat_id")
                }
            logger.info(f"Loaded {len(REPLY_DATA)} auto-replies")

    asyncio.create_task(load_triggers())

# ============================================
# .autoreply Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.autoreply\s+(.+)$", outgoing=True))
    async def add_reply_handler(event):
        if event.sender_id != owner_id:
            return
            
        input_str = event.pattern_match.group(1).strip()
        trigger = ""
        response_text = None
        
        # Parse trigger (support quotes for multi-word/multi-line)
        if input_str.startswith(('"', "'")):
            quote = input_str[0]
            match = re.match(rf"{quote}(.*?){quote}(?:\s*\|\s*(.*))?", input_str, re.DOTALL)
            if match:
                trigger = match.group(1).strip().lower()
                response_text = match.group(2).strip() if match.group(2) else None
        else:
            if "|" in input_str:
                parts = input_str.split("|", 1)
                trigger = parts[0].strip().lower()
                response_text = parts[1].strip()
            else:
                trigger = input_str.lower()

        if not trigger:
            await event.edit("<blockquote><b>Invalid format</b>\n\nUse: <code>.autoreply trigger | response</code>\nOr: <code>.autoreply \"multi word trigger\" | response</code></blockquote>")
            return

        # Handle Reply (Media/Post support)
        msg_id = None
        chat_id = None
        
        if event.is_reply:
            reply = await event.get_reply_message()
            # We save the message ID and chat ID to "forward" or "re-send" it later
            # For better reliability, we can copy the message to Saved Messages
            saved = await ether.send_message("me", reply)
            msg_id = saved.id
            chat_id = "me"
            if not response_text:
                response_text = "[Saved Post/Media]"
        
        if not response_text and not msg_id:
            await event.edit("<blockquote><b>No response provided</b>\n\nProvide text after <code>|</code> or reply to a message.</blockquote>")
            return

        # Save to memory and DB
        REPLY_DATA[trigger] = {
            "text": response_text,
            "msg_id": msg_id,
            "chat_id": chat_id
        }
        
        if db is not None:
            await db.autoreplies.update_one(
                {"trigger": trigger},
                {"$set": {
                    "text": response_text,
                    "msg_id": msg_id,
                    "chat_id": chat_id
                }},
                upsert=True
            )
            
        await event.edit(f"<blockquote><b>Auto-Reply Set</b>\n\n<b>Trigger:</b> {trigger}\n<b>Response:</b> {response_text or 'Media Post'}</blockquote>")

# ============================================
# .delreply Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.delreply\s+(.+)$", outgoing=True))
    async def del_reply_handler(event):
        if event.sender_id != owner_id:
            return
            
        trigger = event.pattern_match.group(1).strip().lower()
        if trigger.startswith(('"', "'")):
            trigger = trigger[1:-1].lower()
        
        if trigger in REPLY_DATA:
            del REPLY_DATA[trigger]
            if db is not None:
                await db.autoreplies.delete_one({"trigger": trigger})
            await event.edit(f"<blockquote><b>Auto-Reply Deleted:</b> {trigger}</blockquote>")
        else:
            await event.edit(f"<blockquote><b>Trigger not found:</b> {trigger}</blockquote>")

# ============================================
# .replies Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.replies$", outgoing=True))
    async def list_replies_handler(event):
        if event.sender_id != owner_id:
            return
            
        if not REPLY_DATA:
            await event.edit("<blockquote>No auto-replies configured.</blockquote>")
            return
            
        msg = "<blockquote><b>Active Auto-Replies</b>\n\n"
        for trigger, data in REPLY_DATA.items():
            resp = data["text"][:30] + "..." if data["text"] and len(data["text"]) > 30 else (data["text"] or "Media Post")
            msg += f"• <b>{trigger}:</b> {resp}\n"
        msg += "</blockquote>"
        
        await event.edit(msg)

# ============================================
# Listener Logic
# ============================================

    @ether.on(events.NewMessage(incoming=True))
    async def reply_listener(event):
        if not REPLY_DATA or not event.is_private:
            return
            
        user_id = event.sender_id
        if user_id == owner_id:
            return
            
        text = event.text.lower()
        if text in REPLY_DATA:
            # Check Rate Limit
            now = time.time()
            if user_id in COOLDOWN_DATA:
                if now - COOLDOWN_DATA[user_id] < COOLDOWN_TIME:
                    return # Still in cool-down
            
            COOLDOWN_DATA[user_id] = now
            data = REPLY_DATA[text]
            
            if data["msg_id"] and data["chat_id"]:
                # Send saved post/media
                try:
                    await ether.send_message(
                        event.chat_id,
                        file=await ether.get_messages(data["chat_id"], ids=data["msg_id"])
                    )
                except Exception as e:
                    logger.error(f"Failed to send auto-reply media: {e}")
                    if data["text"]:
                        await event.reply(data["text"])
            elif data["text"]:
                await event.reply(data["text"])

# ============================================
# .schedule Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.schedule\s+(\d+)\s*\|\s*(.+)$", outgoing=True))
    async def schedule_handler(event):
        if event.sender_id != owner_id:
            return
            
        seconds = int(event.pattern_match.group(1))
        text = event.pattern_match.group(2).strip()
        
        await event.edit(f"<blockquote><b>Message Scheduled</b>\n\n<b>In:</b> {seconds}s\n<b>Text:</b> {text}</blockquote>")
        
        await asyncio.sleep(seconds)
        await ether.send_message(event.chat_id, text)

    logger.info("Auto-Reply plugin loaded (Advanced mode)")
