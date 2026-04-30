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

from telethon import events, Button
import re

from services.shortcut_service import ShortcutService
from utils.parser import parse_links
from utils.logger import get_logger
from core.bot import bot, SHORTCUT_DATA

logger = get_logger("EtherShortcut")


def setup(ether, db, owner_id):
    
    shortcut_service = ShortcutService(db)
    bot_username = None
    try:
        from config.config import Config
        bot_username = Config.BOT_USERNAME
    except:
        pass

# ============================================
# Load Shortcuts Data
# ============================================
    
    async def load_shortcuts_data():
        try:
            if db is None:
                logger.warning("No database, skipping shortcut data load")
                return
            
            shortcuts_collection = db["shortcuts"]
            cursor = shortcuts_collection.find({"owner_id": owner_id})
            shortcuts = await cursor.to_list(length=None)
            
            for shortcut in shortcuts:
                name = shortcut.get("name", "").lower()
                if name:
                    SHORTCUT_DATA[name] = {
                        "text": shortcut.get("text", ""),
                        "image": shortcut.get("image"),
                        "buttons": shortcut.get("buttons")
                    }
                    logger.info(f"Loaded shortcut '{name}' into cache")
            
            logger.info(f"Loaded {len(SHORTCUT_DATA)} shortcuts from database")
        except Exception as e:
            logger.error(f"Failed to load shortcuts data: {e}")
    
    import asyncio
    asyncio.create_task(load_shortcuts_data())


# ============================================
# Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shortcut (\w+)$", outgoing=True))
    async def shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        if not event.is_reply:
            await event.reply(
                "⚠️ Reply to the message you want to save as a shortcut.\n\n"
                "📝 <b>Supported:</b>\n"
                "• Text with **bold**, __italic__, `code`\n"
                "• Images (photos)\n"
                "• Inline buttons (URL or callback)\n\n"
                "📌 <b>Button Format:</b>\n"
                "<code>[Button.url('🌐 My Site', 'https://example.com')]</code>\n"
                "💡 <b>Tip:</b> Include button code in your message text."
            )
            return
        
        msg = await event.get_reply_message()
        
        image_path = None
        if msg.photo:
            try:
                image_path = await msg.download_media(file=f"media/shortcut_{name}.jpg")
                logger.info(f"Shortcut image saved: {image_path}")
            except Exception as e:
                logger.error(f"Failed to download shortcut image: {e}")
        
        raw_text = msg.text or ""
        parsed_text = parse_links(raw_text)
        
        parsed_text = re.sub(r'\[Button\.(url|inline)\([^\]]+\)\]', '', parsed_text).strip()
        
        parsed_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', parsed_text)
        parsed_text = re.sub(r'__(.+?)__', r'<i>\1</i>', parsed_text)
        parsed_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', parsed_text)
        
        buttons = None
        
        if msg.reply_markup:
            from telethon.tl.types import KeyboardButtonRow, KeyboardButtonUrl, KeyboardButtonCallback
            
            button_rows = []
            if hasattr(msg.reply_markup, 'rows'):
                for row in msg.reply_markup.rows:
                    row_buttons = []
                    for btn in row.buttons:
                        if isinstance(btn, KeyboardButtonUrl):
                            row_buttons.append({"text": btn.text, "url": btn.url, "type": "url"})
                        elif isinstance(btn, KeyboardButtonCallback):
                            row_buttons.append({"text": btn.text, "data": btn.data.decode(), "type": "callback"})
                    if row_buttons:
                        button_rows.append(row)
            
            if button_rows:
                buttons = button_rows
                logger.info(f"Shortcut buttons extracted from markup: {len(button_rows)} rows")
        
        if not buttons:
            text_content = msg.text or ""
            logger.info(f"Parsing buttons from text. Text length: {len(text_content)}")
            
            button_pattern = r"\[Button\.(url|inline)\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)\]"
            matches = re.findall(button_pattern, text_content)
            
            logger.info(f"Found {len(matches)} button matches")
            
            if matches:
                lines = text_content.split('\n')
                button_rows = []
                
                for line in lines:
                    line_buttons = []
                    line_matches = re.findall(button_pattern, line)
                    
                    for match in line_matches:
                        btn_type = match[0]
                        text = match[1]
                        value = match[2]
                        
                        if btn_type == 'url':
                            line_buttons.append({"text": text, "url": value, "type": "url"})
                            logger.info(f"Added URL button to row: {text} -> {value}")
                        elif btn_type == 'inline':
                            if value.startswith('b') and len(value) > 1:
                                value = value[1:]
                            line_buttons.append({"text": text, "data": value, "type": "callback"})
                            logger.info(f"Added inline button to row: {text} -> {value}")
                    
                    if line_buttons:
                        button_rows.append(line_buttons)
                
                if button_rows:
                    buttons = button_rows
                    logger.info(f"Shortcut buttons parsed from text: {len(button_rows)} rows")
        
        try:
            await shortcut_service.save_shortcut(owner_id, name, parsed_text, image_path, buttons)
            
            SHORTCUT_DATA[name.lower()] = {
                "text": parsed_text,
                "image": image_path,
                "buttons": buttons
            }
            
            response = f"✅ Shortcut '{name}' saved."
            if image_path:
                response += "\n📷 Image included."
            if buttons:
                response += f"\n🔘 {len(buttons)} button rows included."
            await event.edit(response)
            logger.info(f"Shortcut '{name}' saved by owner")
        except Exception as e:
            logger.error(f"Failed to save shortcut: {e}")
            await event.edit("❌ Failed to save shortcut.")


# ============================================
# Get Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.get (\w+)$", outgoing=True))
    async def get_shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        shortcut = await shortcut_service.get_shortcut(owner_id, name)
        
        if not shortcut:
            await event.reply(f"❌ Shortcut '{name}' not found.")
            logger.info(f"Shortcut '{name}' not found")
            return
        
        text = shortcut.get("text", "")
        image = shortcut.get("image")
        buttons = shortcut.get("buttons")
        
        async def send_shortcut_message(text: str, target_chat=None) -> None:
            try:
                chat_id = target_chat or event.chat_id
                
                if bot_username and buttons:
                    logger.info(f"Attempting bot inline send for shortcut '{name}'")
                    
                    try:
                        results = await ether.inline_query(bot_username, f"shortcut:{name.lower()}")
                        logger.info(f"Inline query returned {len(results)} results")
                        
                        if results:
                            await results[0].click(chat_id)
                            logger.info(f"Shortcut '{name}' sent via bot inline to {chat_id}")
                            return
                        else:
                            logger.warning("No inline query results returned")
                    except Exception as inline_err:
                        logger.error(f"Inline query failed: {inline_err}")
                
                logger.info(f"Falling back to userbot send for shortcut '{name}'")
                if image:
                    await ether.send_file(chat_id, file=image, caption=text, parse_mode="html")
                else:
                    await ether.send_message(chat_id, text, parse_mode="html")
            except Exception as e:
                logger.error(f"Failed to send shortcut: {e}")
                try:
                    await ether.send_message(chat_id, text)
                except Exception as e2:
                    logger.error(f"Failed to send fallback: {e2}")
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            target_chat = reply_msg.chat_id
            await send_shortcut_message(text, target_chat)
            await event.edit(f"✅ Shortcut '{name}' sent.")
            logger.info(f"Shortcut '{name}' sent to chat {target_chat}")
        else:
            await send_shortcut_message(text)
            await event.edit(f"✅ Shortcut '{name}' sent.")
            logger.info(f"Shortcut '{name}' sent to current chat")


# ============================================
# Delete Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.delshortcut (\w+)$", outgoing=True))
    async def del_shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        deleted = await shortcut_service.delete_shortcut(owner_id, name)
        
        if deleted:
            if name.lower() in SHORTCUT_DATA:
                del SHORTCUT_DATA[name.lower()]
            
            await event.edit(f"🗑️ Shortcut '{name}' deleted.")
            logger.info(f"Shortcut '{name}' deleted by owner")
        else:
            await event.edit(f"❌ Shortcut '{name}' not found.")
            logger.info(f"Shortcut '{name}' not found for deletion")
    
# ============================================
# List Shortcuts Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shortcuts$", outgoing=True))
    async def list_shortcuts_handler(event):
        if event.sender_id != owner_id:
            return
        
        shortcuts = await shortcut_service.list_shortcuts(owner_id)
        
        if not shortcuts:
            await event.reply("📭 No shortcuts saved yet.\n\nUse .shortcut <name> to save one.")
            logger.info("No shortcuts found")
        else:
            shortcut_list = "\n".join(f"• <code>{s}</code>" for s in shortcuts)
            await event.reply(f"📋 <b>Your Shortcuts:</b>\n\n{shortcut_list}\n\n<i>Total: {len(shortcuts)}</i>", parse_mode="html")
            logger.info(f"Listed {len(shortcuts)} shortcuts")
    
    logger.info("Shortcut plugin loaded")
