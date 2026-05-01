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

from telethon import events
import asyncio

def setup(ether, db, owner_id):

    BATCH_SIZE = 1          # users per message
    DELAY = 3              # seconds between batches
    MAX_USERS = 100        # safety limit

# ============================================
# Tagall Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.tagall(?:\s+(.+))?$", outgoing=True))
    async def tagall_handler(event):
        
        #  OWNER ONLY
        if event.sender_id != owner_id:
            return
        
        if not event.is_group:
            await event.reply("This command works only in groups.")
            return
        
        message = event.pattern_match.group(1) or "Hello!"
        
        await event.reply("Starting TagAll... (safe mode)")
        
        users = []
        
        # Fetch participants safely
        async for user in ether.iter_participants(event.chat_id):
            if user.bot or user.deleted:
                continue
            users.append(user)
        
        if not users:
            await event.reply("No users found.")
            return
        
        # Apply safety limit
        users = users[:MAX_USERS]
        
        total = len(users)
        sent = 0
        
        # Batch sending
        for i in range(0, total, BATCH_SIZE):
            batch = users[i:i + BATCH_SIZE]
            
            mentions = []
            for user in batch:
                name = user.first_name or "User"
                mention = f"[{name}](tg://user?id={user.id})"
                mentions.append(mention)
            
            text = message + "\n\n" + " ".join(mentions)
            
            try:
                await ether.send_message(
                    event.chat_id,
                    text,
                    parse_mode="md"
                )
                sent += len(batch)
            except Exception as e:
                print(f"Tag batch failed: {e}")
            
            await asyncio.sleep(DELAY)
        
        await event.reply(f"TagAll completed. Tagged {sent} users safely.")