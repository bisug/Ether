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

from telethon import events, errors
import asyncio
from utils.logger import get_logger

logger = get_logger("EtherTagAll")

# Track active tagall tasks to allow stopping them
# Format: {chat_id: True/False}
ACTIVE_TASKS = {}

def setup(ether, db, owner_id):

    BATCH_SIZE = 5          # users per message
    DELAY = 2               # seconds between batches
    MAX_USERS = 250         # safety limit

# ============================================
# Tagall Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.tagall(?:(?:\s+)(.+))?$", outgoing=True))
    async def tagall_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_group:
            await event.edit("<blockquote><b>Command Error:</b> This command works only in groups.</blockquote>")
            return

        arg = event.pattern_match.group(1)
        
        # Check for stop command
        if arg and arg.lower() == "stop":
            if event.chat_id in ACTIVE_TASKS:
                ACTIVE_TASKS[event.chat_id] = False
                await event.edit("<blockquote><b>Action Success:</b> Stopping TagAll...</blockquote>")
            else:
                await event.edit("<blockquote><b>Command Error:</b> No active TagAll in this chat.</blockquote>")
            return

        # Start TagAll
        message = arg or "Hey everyone!"
        
        if event.chat_id in ACTIVE_TASKS and ACTIVE_TASKS[event.chat_id]:
            await event.edit("<blockquote><b>Process Error:</b> A TagAll is already running in this chat.</blockquote>")
            return

        await event.delete()
        status_msg = await ether.send_message(
            event.chat_id, 
            "<blockquote><b>Starting TagAll...</b>\n<i>Use <code>.tagall stop</code> to cancel.</i></blockquote>"
        )
        
        ACTIVE_TASKS[event.chat_id] = True
        
        try:
            users = []
            async for user in ether.iter_participants(event.chat_id):
                if user.bot or user.deleted:
                    continue
                users.append(user)
            
            if not users:
                await status_msg.edit("<blockquote><b>Process Error:</b> No eligible users found.</blockquote>")
                return

            users = users[:MAX_USERS]
            total = len(users)
            sent = 0
            
            for i in range(0, total, BATCH_SIZE):
                # Check if task was cancelled
                if not ACTIVE_TASKS.get(event.chat_id):
                    break
                
                batch = users[i:i + BATCH_SIZE]
                mentions = []
                for user in batch:
                    name = user.first_name or "User"
                    mentions.append(f"[{name}](tg://user?id={user.id})")
                
                tag_text = f"<b>Broadcast:</b> {message}\n\n" + " ".join(mentions)
                
                try:
                    await ether.send_message(event.chat_id, tag_text)
                    sent += len(batch)
                except errors.FloodWaitError as e:
                    logger.warning(f"FloodWait: Sleeping for {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.error(f"Tag error: {e}")
                
                await asyncio.sleep(DELAY)
            
            result_text = f"<blockquote><b>TagAll Completed</b>\nTagged: {sent} users</blockquote>"
            if not ACTIVE_TASKS.get(event.chat_id):
                result_text = f"<blockquote><b>TagAll Stopped</b>\nTagged: {sent} users</blockquote>"
            
            await ether.send_message(event.chat_id, result_text)
            
        finally:
            ACTIVE_TASKS[event.chat_id] = False
            try:
                await status_msg.delete()
            except:
                pass

    logger.info("Enhanced TagAll plugin loaded")
