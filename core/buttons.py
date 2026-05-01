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

import random
import os
import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from storage.mongo import ether_db
from utils.encryption import encrypt_session, decrypt_session
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError
)
from config.config import Config
from config.channels import get_channel_list, get_channels
from utils.logger import get_logger
from services.dm_shield_service import DMShieldService
from core.user_client import EtherUserClient

logger = get_logger("EtherBot")

bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)

# Store login state temporarily
login_state = {}
userbot_wrapper = EtherUserClient()
userbot_client = userbot_wrapper.get_client()
plugin_loader = None
cloned_clients = {} # {user_id: client}

HELP_DATA = {
    "text": "<b>Ether Userbot Help Guide</b>",
    "buttons": None
}

WELCOME_DATA = {
    "text": None,
    "image": None,
    "buttons": None
}

SHORTCUT_DATA = {}


main_buttons = [
    [
        Button.inline("DM Protection", b"help_dm"),
        Button.inline("Shortcuts", b"help_shortcut")
    ],
    [
        Button.inline("TagAll", b"help_tagall"),
        Button.inline("Fonts", b"help_fonts")
    ],
    [
        Button.inline("DM Shield", b"help_shield"),
        Button.inline("Bot Commands", b"help_bot")
    ],
    [
        Button.inline("Ping System", b"help_ping"),
        Button.inline("System Info", b"help_system")
    ]
]


HELP_DATA["buttons"] = main_buttons

# ============================================

def get_bot_name():
    return ether_bot.me.first_name if ether_bot and ether_bot.me else "Ether Userbot"

def get_userbot_name():
    return userbot_wrapper.me.first_name if userbot_wrapper and userbot_wrapper.me else "Ether User"

def update_dynamic_texts():
    global BOT_WELCOME_TEXT, HELP_DATA

    bot_name = get_bot_name()
    userbot_name = get_userbot_name()

    HELP_DATA["text"] = f"<b>{bot_name} Help Guide</b>"

    BOT_WELCOME_TEXT = (
        f"<b>Welcome to {bot_name} System</b>\n\n"
        f"{bot_name} is a high-performance, modular Telegram userbot architecture built with Telethon and MongoDB. Designed for developers who prioritize security, speed, and clean code.\n\n"
        "<b>Security:</b> 99% safe - no need to generate session strings from unknown sources.\n"
        "For full transparency, check the source code below.\n\n"
        "Manage your Telegram account like a pro with automation and control."
    )

@bot.on(events.InlineQuery)
async def inline_help(event):
    if event.text == "help":
        builder = event.builder
        
        bot_name = get_bot_name()
        result = builder.article(
            id="help_menu",
            title=f"{bot_name} Help Menu",
            description="Click to see help with buttons",
            text=f"<b>{bot_name} Help Guide</b>\n\nWelcome to the help center. Select a category below to view available commands and their usage guides:",
            buttons=main_buttons,
            parse_mode="html"
        )
        
        await event.answer([result], cache_time=0)
        logger.info(f"Inline help for user {event.sender_id}")

# ============================================

    elif event.text == "welcome":
        logger.info(f"Welcome inline query from user {event.sender_id}")
        if WELCOME_DATA["text"]:
            try:
                builder = event.builder
                
                buttons = None
                if WELCOME_DATA["buttons"]:
                    logger.info(f"Reconstructing {len(WELCOME_DATA['buttons'])} button rows")
                    button_rows = []
                    for i, row in enumerate(WELCOME_DATA["buttons"]):
                        row_buttons = []
                        logger.info(f"Processing row {i}: {type(row)} - {row}")
                        for btn in row:
                            logger.info(f"Processing button: {type(btn)} - {btn}")
                            if isinstance(btn, dict):
                                if btn.get("type") == "url":
                                    row_buttons.append(Button.url(btn["text"], btn["url"]))
                                    logger.info(f"Added URL button: {btn['text']}")
                                elif btn.get("type") == "callback":
                                    data = btn["data"]
                                    if isinstance(data, str):
                                        data = data.encode('utf-8')
                                    elif not isinstance(data, bytes):
                                        data = str(data).encode('utf-8')
                                    row_buttons.append(Button.inline(btn["text"], data))
                                    logger.info(f"Added inline button: {btn['text']}")
                            else:
                                logger.warning(f"Unexpected button type: {type(btn)}")
                        if row_buttons:
                            button_rows.append(row_buttons)
                            logger.info(f"Added row with {len(row_buttons)} buttons")
                    
                    if button_rows:
                        buttons = button_rows
                        logger.info(f"Total button rows: {len(button_rows)}")
                
                
                if WELCOME_DATA["image"]:
                    result = builder.photo(
                        file=WELCOME_DATA["image"],
                        id="welcome_msg",
                        text=WELCOME_DATA["text"],
                        buttons=buttons,
                        parse_mode="html"
                    )
                else:
                    result = builder.article(
                        id="welcome_msg",
                        title="Welcome Message",
                        description="DM Protection Welcome",
                        text=WELCOME_DATA["text"],
                        buttons=buttons,
                        parse_mode="html"
                    )
                
                await event.answer([result], cache_time=0)
            except Exception as e:
                logger.error(f"Failed to create welcome inline result: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"WELCOME_DATA is empty, cannot answer inline query")

# ============================================

    elif event.text.startswith("shortcut:"):
        shortcut_name = event.text.replace("shortcut:", "").lower()
        
        if shortcut_name in SHORTCUT_DATA:
            try:
                builder = event.builder
                shortcut = SHORTCUT_DATA[shortcut_name]
                
                buttons = None
                if shortcut.get("buttons"):
                    button_rows = []
                    for i, row in enumerate(shortcut["buttons"]):
                        row_buttons = []
                        for btn in row:
                            if isinstance(btn, dict):
                                if btn.get("type") == "url":
                                    row_buttons.append(Button.url(btn["text"], btn["url"]))
                                    logger.info(f"Added URL button: {btn['text']}")
                                elif btn.get("type") == "callback":
                                    data = btn["data"]
                                    if isinstance(data, str):
                                        data = data.encode('utf-8')
                                    elif not isinstance(data, bytes):
                                        data = str(data).encode('utf-8')
                                    row_buttons.append(Button.inline(btn["text"], data))
                                    logger.info(f"Added inline button: {btn['text']}")
                        if row_buttons:
                            button_rows.append(row_buttons)
                    
                    if button_rows:
                        buttons = button_rows
                
                text = shortcut.get("text", "")
                image = shortcut.get("image")
                
                
                if image:
                    result = builder.photo(
                        file=image,
                        id=f"shortcut_{shortcut_name}",
                        text=text,
                        buttons=buttons,
                        parse_mode="html"
                    )
                else:
                    result = builder.article(
                        id=f"shortcut_{shortcut_name}",
                        title=f"Shortcut: {shortcut_name}",
                        description="Saved shortcut content",
                        text=text,
                        buttons=buttons,
                        parse_mode="html"
                    )
                
                await event.answer([result], cache_time=0)
            except Exception as e:
                logger.error(f"Failed to create shortcut inline result: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"Shortcut '{shortcut_name}' not found in SHORTCUT_DATA")

# ============================================

    elif event.text.startswith("fonts:"):
        try:
            text = event.text.replace("fonts:", "", 1)

            builder = event.builder

            result_text = "<b>Font Styles</b>\n\n"

            for key in FONT_MAPS:
                styled = apply_font(text, key)
                result_text += f"{key} -> <code>{styled}</code>\n"

            buttons = [
                [
                    Button.inline("Style", f"font_style:{text}".encode()),
                    Button.inline("Mix", f"font_mix:{text}".encode())
                ]
            ]

            result = builder.article(
                id="font_preview",
                title="Font Styles",
                description="Preview styled text",
                text=result_text,
                buttons=buttons,
                parse_mode="html"
            )

            await event.answer([result], cache_time=0)

        except Exception as e:
            logger.error(f"Font inline error: {e}")

# ============================================

    elif event.text == "alive":
        builder = event.builder

        bot_name = get_bot_name()
        userbot_name = get_userbot_name()
    
        result = builder.photo(
            file=Config.START_IMG_URL,
            text=(
                f"<b>{userbot_name} is Alive</b>\n\n"
                "<blockquote>"
                "Status: ONLINE\n"
                "System: RUNNING\n"
                "DM Shield: ACTIVE\n"
                "Telethon: CONNECTED\n"
                "Database: STABLE\n"
                "</blockquote>\n\n"
                "<i>All systems operational</i>"
            ),
            buttons=[
                [
                    Button.url("Repository", "https://github.com/LearningBotsOfficial/Ether")
                ]
            ],
            parse_mode="html"
        )

        await event.answer([result], cache_time=0)
    
    

# ============================================
# Callback Handlers
# ============================================

@bot.on(events.CallbackQuery(data=b"help_back"))
async def cb_back(event):
    bot_name = get_bot_name()
    await event.edit(
        f"<b>{bot_name} Help Guide</b>\n\nWelcome to the help center. Select a category below to view available commands and their usage guides:",
        buttons=main_buttons,
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_dm"))
async def cb_dm(event):
    await event.edit(
        "<b>DM Protection System</b>\n\n"
        "<b>Overview:</b>\n"
        "When someone messages you:\n"
        "1. First message -> Welcome message sent\n"
        "2. Follow-ups -> Warning counter (max 3)\n"
        "3. After max warnings -> Auto block\n\n"
        "Only users you <code>.allow</code> can message freely.\n\n"
        "<b>Commands:</b>\n"
        "<code>.setwelcome</code> - Set welcome message with buttons\n"
        "<code>.clearwelcome</code> - Remove welcome message\n"
        "<code>.allow</code> - Allow user (in their DM)\n"
        "<code>.disallow</code> - Disallow user (in their DM)\n"
        "<code>.setwarn &lt;number&gt;</code> - Set max warnings\n\n"
        "<b>Warning System:</b>\n"
        "Users who aren't allowed get:\n"
        "- Welcome on 1st message\n"
        "- Warning X/N on follow-ups\n"
        "- <b>Auto-block</b> at max warnings\n\n"
        "Use <code>.setwarn &lt;number&gt;</code> to change limit",
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_shortcut"))
async def cb_shortcut(event):
    await event.edit(
        "<b>Shortcuts System</b>\n\n"
        "<b>Overview:</b>\n"
        "Save messages, images, and buttons with custom names for quick access.\n"
        "- <b>Text:</b> Save formatted text with bold, italic, code\n"
        "- <b>Images:</b> Save photos with captions\n"
        "- <b>Buttons:</b> Save inline buttons (URL & callback)\n\n"
        "Perfect for welcome messages, announcements, or frequently sent content.\n\n"
        "<b>Commands:</b>\n"
        "<code>.shortcut &lt;name&gt;</code> - Save content (reply to message)\n"
        "<code>.get &lt;name&gt;</code> - Retrieve and send shortcut\n"
        "<code>.delshortcut &lt;name&gt;</code> - Delete a shortcut\n"
        "<code>.shortcuts</code> - List all saved shortcuts\n\n"
        "<b>Tips:</b>\n"
        "- Reply to a message with <code>.shortcut mychannel</code> to save\n"
        "- Use <code>.get mychannel</code> to send it anywhere\n"
        "- Reply to a message with <code>.get mychannel</code> to send to that chat\n"
        "- Names are case-insensitive (MyChannel = mychannel)\n"
        "- Button format: <code>[Button.url('Text', 'URL')]</code>\n"
        "- Button format: <code>[Button.inline('Text', 'data')]</code>",
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_tagall"))
async def cb_tagall(event):
    await event.edit(
        "<b>TagAll</b>\n\n"
        "Mention group members in small batches with delay to avoid spam and limits.\n\n"
        
        "<b>Command:</b>\n"
        "<code>.tagall</code>\n\n"
        
        "<b>Example:</b>\n"
        "<code>.tagall Hello everyone!</code>\n\n"
        
        "<b>Tips:</b>\n"
        "- Works only in groups\n"
        "- Skips bots & deleted users\n"
        "- Uses safe limits to protect your account",
        
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_ping"))
async def cb_ping(event):
    await event.edit(
        "<b>Ping System</b>\n\n"
        "<b>Overview:</b>\n"
        "The ping command measures how quickly the userbot responds.\n"
        "Lower = better.\n\n"
        "<b>Commands:</b>\n"
        "<code>.ping</code> - Check response time\n\n"
        "Returns time in milliseconds.",
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_system"))
async def cb_system(event):
    bot_name = get_bot_name()
    userbot_name = get_userbot_name()
    await event.edit(
        f"<b>System Information</b>\n\n"
        f"{userbot_name} ({bot_name}) v2.0\n"
        "- Telethon\n"
        "- MongoDB\n"
        "- Plugins\n\n"
        "<b>Commands:</b>\n"
        "<code>.alive</code> - View system status and uptime",
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_fonts"))
async def cb_fonts(event):
    await event.edit(
        "<b>Fonts & Styles System</b>\n\n"
        "<b>Overview:</b>\n"
        "Convert normal text into stylish fonts and modern effects.\n"
        "Includes aesthetic, glitch, hacker, and decorative styles.\n\n"
        
        "<b>Command:</b>\n"
        "<code>.fonts &lt;text&gt;</code>\n\n"
        
        "<b>Example:</b>\n"
        "<code>.fonts hello world</code>\n\n"
        
        "<b>Features:</b>\n"
        "- 10+ Unicode font styles\n"
        "- Aesthetic & vaporwave text\n"
        "- Glitch & hacker effects\n"
        "- Mix styles randomly\n"
        "- Interactive buttons (Style / Mix / Cool)\n\n"
        
        "<b>Tips:</b>\n"
        "- Works in any chat\n"
        "- Use for bios, captions, branding\n"
        "- Combine with shortcuts for fast reuse",
        
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================

@bot.on(events.CallbackQuery(pattern=b"font_.*"))
async def font_callbacks(event):

    data = event.data.decode()

    if data.startswith("font_style:"):
        text = data.split(":", 1)[1]

        result = (
            f"<code>{text}</code>\n"
            f"<code>{apply_font(text,'2')}</code>\n"
            f"<code>{apply_font(text,'3')}</code>"
        )

        await event.edit(result, parse_mode="html")

    elif data.startswith("font_mix:"):
        text = data.split(":", 1)[1]

        mixed = ""
        for char in text:
            if char.isalpha():
                font = random.choice(list(FONT_MAPS.keys()))
                mixed += char.lower().translate(FONT_MAPS[font])
            else:
                mixed += char

        await event.edit(
            f"<b>Mixed Style</b>\n\n<code>{mixed}</code>",
            parse_mode="html"
        )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_shield"))
async def cb_shield(event):

    await event.edit(
        "<b>DM Shield System</b>\n\n"
        
        "<b>Overview:</b>\n"
        "Automatically protects your DM from unwanted messages.\n\n"
        
        "<b>What it blocks:</b>\n"
        "- Links (t.me, https, tg://)\n"
        "- Usernames (@spam tags)\n\n"
        
        "<b>Commands:</b>\n"
        "<code>.shield</code> - Open control panel\n"
        "<code>.shield on</code> - Enable system\n"
        "<code>.shield off</code> - Disable system\n"
        "<code>.shield link</code> - link filter\n"
        "<code>.shield user</code> - username filter\n"
        "<code>.shield allow</code> - Reply to whitelist user\n"
        "<code>.shield disallow</code> - Reply to remove whitelist\n"
        "<code>.shield status</code> - Show system status\n\n"
        
        "<b>Tip:</b>\n"
        "Use allow system to whitelist trusted users.",
        
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )


# ============================================

@bot.on(events.CallbackQuery(data=b"help_bot"))
async def cb_bot(event):
    await event.edit(
        "<b>Bot Commands</b>\n\n"
        "<b>Overview:</b>\n"
        "Commands to manage the bot and your session.\n\n"
        "<b>Commands:</b>\n"
        "<code>/start</code> - Initialize the bot and view welcome message\n"
        "<code>/help</code> - View help menu\n"
        "<code>/login</code> - Securely authenticate your account (Admin only)\n"
        "<code>/clone</code> - Instructions & risk info for cloning\n"
        "<code>/clone &lt;session&gt;</code> - Clone a userbot instance\n"
        "<code>/cancel</code> - Cancel ongoing login process (Admin only)\n"
        "<code>/remove</code> - Select an account to remove from system",
        buttons=[[Button.inline("Back", b"help_back")]],
        parse_mode="html"
    )

# ============================================
# Bot Welcome
# ============================================

BOT_WELCOME_TEXT = (
    "<b>Welcome to Ether Userbot System</b>\n\n"
    "Ether is a high-performance, modular Telegram userbot architecture built with Telethon and MongoDB. Designed for developers who prioritize security, speed, and clean code.\n\n"
    "<b>Security:</b> 99% safe - no need to generate session strings from unknown sources.\n"
    "For full transparency, check the source code below.\n\n"
    "Manage your Telegram account like a pro with automation and control."
)

BOT_WELCOME_IMAGE = Config.START_IMG_URL

bot_dm_buttons = [
    [
        Button.url("Updates", "https://t.me/Ether_Update"),
        Button.url("Support Group", "https://t.me/EtherSupport")
    ],
    [
        Button.url("Source Code", "https://github.com/LearningBotsOfficial/Ether"),
        Button.inline("Help Menu", b"help_back")
    ],
]

# ============================================
# Bot Start Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/help$", incoming=True, func=lambda e: e.is_private))
async def bot_help_handler(event):
    bot_name = get_bot_name()
    try:
        await bot.send_message(
            event.chat_id,
            f"<b>{bot_name} Help Guide</b>\n\nWelcome to the help center. Select a category below to view available commands and their usage guides:",
            buttons=main_buttons,
            parse_mode="html"
        )
    except Exception as e:
        logger.error(f"Bot /help reply failed: {e}")


@bot.on(events.NewMessage(pattern=r"^/start$", incoming=True, func=lambda e: e.is_private))
async def bot_start_handler(event):
    try:
        await bot.send_file(
            event.chat_id,
            file=BOT_WELCOME_IMAGE,
            caption=BOT_WELCOME_TEXT,
            buttons=bot_dm_buttons,
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Bot /start reply failed: {e}", exc_info=True)

        try:
            await bot.send_message(
                event.chat_id,
                BOT_WELCOME_TEXT,
                buttons=bot_dm_buttons,
                parse_mode="html"
            )
            logger.info(f"Bot /start fallback sent to user {event.sender_id}")
        except Exception as e2:
            logger.error(f"Bot /start fallback failed: {e2}", exc_info=True)


# ============================================
# Bot Login Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/login$", incoming=True, func=lambda e: e.is_private))
async def bot_login_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply("This command is only for the admin.")
        return
    
    if userbot_client is None:
        await event.reply("Userbot client not initialized. Please restart the bot.")
        return
    
    login_state[Config.OWNER_ID] = {"step": "phone"}
    
    bot_name = get_bot_name()
    await event.reply(
        f"<b>{bot_name} Login System</b>\n\n"
        "Please enter your phone number with country code.\n\n"
        "<i>Example: +9198*****</i>\n\n"
        "Send /cancel to abort.",
        parse_mode="html"
    )
    logger.info(f"Login initiated by owner {Config.OWNER_ID}")

# ============================================
# Bot Clone Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/clone(?:\s+(.+))?$", incoming=True, func=lambda e: e.is_private))
async def bot_clone_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply("This command is only for the admin.")
        return

    session_string = event.pattern_match.group(1)
    bot_name = get_bot_name()

    if not session_string:
        # Show instructions and risks
        instructions = (
            f"<b>{bot_name} Clone System</b>\n\n"
            "To clone a userbot, use <code>/clone STRING_SESSION</code>\n\n"
            "<b>How to get String Session?</b>\n"
            "Visit: <a href='https://telegram.tools/session-string-generator#telethon,user'>Telegram Tools</a>\n\n"
            "<b>⚠️ IMPORTANT & RISKY</b>\n"
            "String sessions grant full access to your Telegram account. Never share them with anyone.\n"
            "<b>Avoid using unknown bots</b> to generate sessions as they may steal your account.\n"
            "Always use the safe and reliable link provided above."
        )
        await event.reply(instructions, parse_mode="html", link_preview=False)
        return

    # Process clone request

    msg = await event.reply("<i>Validating and cloning userbot...</i>", parse_mode="html")

    try:
        # Try to connect and verify the session string
        temp_client = userbot_wrapper.create_string_client(session_string)
        await temp_client.connect()

        if not await temp_client.is_user_authorized():
            await msg.edit("<b>Invalid Session String</b>\n\nThe provided session string is not authorized or expired.", parse_mode="html")
            await temp_client.disconnect()
            return

        me = await temp_client.get_me()
        user_id = me.id

        # Check if already cloned
        if ether_db.sessions:
            existing = await ether_db.sessions.find_one({"user_id": user_id})
            if existing:
                await msg.edit(f"<b>Account already cloned:</b> {me.first_name}", parse_mode="html")
                await temp_client.disconnect()
                return

            # Encrypt and save to DB
            encrypted = encrypt_session(session_string)
            await ether_db.sessions.insert_one({
                "user_id": user_id,
                "session": encrypted,
                "name": me.first_name,
                "username": me.username,
                "type": "clone",
                "added_by": event.sender_id
            })

            # Start the client and load plugins
            add_cloned_client(user_id, temp_client)

            if plugin_loader:
                plugin_loader.load_all(temp_client)

            # Run in background
            asyncio.create_task(temp_client.run_until_disconnected())

            await msg.edit(
                f"<b>Userbot Cloned Successfully!</b>\n\n"
                f"<b>Account:</b> {me.first_name}\n"
                f"<b>ID:</b> <code>{user_id}</code>\n"
                "Plugins have been loaded for this account.",
                parse_mode="html"
            )
            logger.info(f"Userbot cloned: {me.first_name} ({user_id})")
        else:
            await msg.edit("Database connection not available. Cannot save session.", parse_mode="html")
            await temp_client.disconnect()

    except Exception as e:
        logger.error(f"Clone error: {e}")
        await msg.edit(f"<b>Clone Failed</b>\n\nError: <code>{str(e)}</code>", parse_mode="html")


# ============================================
# Bot Cancel Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/cancel$", incoming=True, func=lambda e: e.is_private))
async def bot_cancel_handler(event):
    if event.sender_id != Config.OWNER_ID:
        return
    
    if Config.OWNER_ID in login_state:
        del login_state[Config.OWNER_ID]
        await event.reply("Login cancelled.")


# ============================================
# Bot Login Flow Handler
# ============================================

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def bot_login_flow_handler(event):
    global userbot_client, userbot_wrapper
    
    if event.sender_id != Config.OWNER_ID:
        return
    
    if Config.OWNER_ID not in login_state:
        return
    
    if userbot_client is None:
        await event.reply("Userbot client not initialized.")
        return
    
    state = login_state[Config.OWNER_ID]
    text = event.text.strip()
    
    if text.startswith("/"):
        return
    
    if state["step"] == "phone":
        phone = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                logger.info("Userbot client not connected, attempting to connect...")
                await userbot_client.connect()
            
            if not userbot_client.is_connected():
                await event.reply("<b>Connection Error</b>\n\nFailed to connect to Telegram servers. Please check your internet connection or API credentials.", parse_mode="html")
                return

            result = await userbot_client.send_code_request(phone)
            state["step"] = "otp"
            state["phone"] = phone
            state["phone_code_hash"] = result.phone_code_hash
            
            await event.reply(
                "Send OTP with spaces (e.g. 1 2 3 4 5)\n\n"
                "Send /cancel to abort.",
                parse_mode="html"
            )
            logger.info(f"OTP sent to {phone}")
        except FloodWaitError as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<b>Flood Wait</b>\n\nPlease wait {e.seconds} seconds before trying again.", parse_mode="html")
            logger.warning(f"Flood wait: {e.seconds}s")
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<b>Error</b>\n\nFailed to send OTP: {str(e)}", parse_mode="html")
            logger.error(f"OTP send error: {e}")
    
    elif state["step"] == "otp":
        code = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                logger.info("Userbot client not connected during OTP step, attempting to connect...")
                await userbot_client.connect()
            
            if not userbot_client.is_connected():
                await event.reply("<b>Connection Error</b>\n\nConnection lost. Please try /login again.", parse_mode="html")
                return

            await userbot_client.sign_in(
                phone=state["phone"],
                code=code,
                phone_code_hash=state["phone_code_hash"]
            )
            
            del login_state[Config.OWNER_ID]
            
            # Save to DB after successful login

            me = await userbot_client.get_me()
            session_str = StringSession.save(userbot_client.session)
            encrypted = encrypt_session(session_str)

            if ether_db.sessions:
                await ether_db.sessions.update_one(
                    {"user_id": me.id},
                    {"$set": {
                        "user_id": me.id,
                        "session": encrypted,
                        "name": me.first_name,
                        "username": me.username,
                        "type": "main"
                    }},
                    upsert=True
                )
                logger.info(f"Main session saved to MongoDB for {me.first_name}")

            await asyncio.sleep(1)
            await userbot_client.disconnect()
            
            if userbot_wrapper:
                userbot_wrapper._client = None
                userbot_client = userbot_wrapper.get_client()
                await userbot_client.connect()
                logger.info("Userbot client recreated and reconnected after login")
            else:
                await userbot_client.connect()
                logger.info("Userbot client reconnected after login (no wrapper)")
            
            # Verify authorization
            is_authorized = await userbot_client.is_user_authorized()
            if is_authorized:
                logger.info("Userbot session verified as authorized")
            else:
                logger.warning("Userbot session not authorized after reconnection")
            
            # Auto-join official channels
            try:
                channels = get_channels()
                joined_count = 0
                for name, link in channels.items():
                    try:
                        # Extract channel username from link
                        username = link.split('/')[-1]
                        await userbot_client(JoinChannelRequest(username))
                        joined_count += 1
                        logger.info(f"Joined channel: {name} ({username})")
                        await asyncio.sleep(1)  # Rate limit
                    except Exception as e:
                        logger.warning(f"Could not join {name}: {e}")
                if joined_count > 0:
                    logger.info(f"Successfully joined {joined_count} official channels")
            except Exception as e:
                logger.error(f"Channel auto-join failed: {e}")
            
            # Reload plugins with new client instance
            if plugin_loader:
                plugin_loader.client = userbot_client
                plugin_loader.load_all()
                stats = plugin_loader.get_stats()
                logger.info(f"Reloaded {stats['total']} plugins after login: {stats['plugins']}")
            else:
                logger.warning("Plugin loader not available - commands may not work")
            
            await event.reply(
                "<b>Login Successful!</b>\n\n"
                "Your session has been created.\n"
                "The userbot has been reconnected.\n"
                "Joined official channels automatically.\n\n"
                "You can now use all commands.",
                parse_mode="html"
            )
            logger.info("Login successful")
        except SessionPasswordNeededError:
            state["step"] = "2fa"
            await event.reply(
                "<b>2FA Required</b>\n\n"
                "Please enter your two-factor authentication password.\n\n"
                "Send /cancel to abort.",
                parse_mode="html"
            )
            logger.info("2FA required")
        except PhoneCodeInvalidError:
            del login_state[Config.OWNER_ID]
            await event.reply("<b>Invalid Code</b>\n\nThe OTP you entered is incorrect. Please try /login again.", parse_mode="html")
            logger.warning("Invalid OTP entered")
        except PhoneCodeExpiredError:
            del login_state[Config.OWNER_ID]
            await event.reply("<b>Code Expired</b>\n\nThe OTP has expired. Please try /login again.", parse_mode="html")
            logger.warning("OTP expired")
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<b>Error</b>\n\nFailed to verify OTP: {str(e)}", parse_mode="html")
            logger.error(f"OTP verify error: {e}")
    
    elif state["step"] == "2fa":
        password = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                logger.info("Userbot client not connected during 2FA step, attempting to connect...")
                await userbot_client.connect()
            
            if not userbot_client.is_connected():
                await event.reply("<b>Connection Error</b>\n\nConnection lost. Please try /login again.", parse_mode="html")
                return

            await userbot_client.sign_in(password=password)
            
            del login_state[Config.OWNER_ID]
            
            # Save to DB after successful login (2FA)

            me = await userbot_client.get_me()
            session_str = StringSession.save(userbot_client.session)
            encrypted = encrypt_session(session_str)

            if ether_db.sessions:
                await ether_db.sessions.update_one(
                    {"user_id": me.id},
                    {"$set": {
                        "user_id": me.id,
                        "session": encrypted,
                        "name": me.first_name,
                        "username": me.username,
                        "type": "main"
                    }},
                    upsert=True
                )
                logger.info(f"Main session (2FA) saved to MongoDB for {me.first_name}")

            await asyncio.sleep(1)
            await userbot_client.disconnect()
            
            if userbot_wrapper:
                userbot_wrapper._client = None
                userbot_client = userbot_wrapper.get_client()
                await userbot_client.connect()
                logger.info("Userbot client recreated and reconnected after 2FA login")
            else:
                await userbot_client.connect()
                logger.info("Userbot client reconnected after 2FA login (no wrapper)")
            
            is_authorized = await userbot_client.is_user_authorized()
            if is_authorized:
                logger.info("Userbot session verified as authorized (2FA)")
            else:
                logger.warning("Userbot session not authorized after 2FA reconnection")
            
            # Auto-join official channels (2FA login)
            try:
                channels = get_channels()
                joined_count = 0
                for name, link in channels.items():
                    try:
                        username = link.split('/')[-1]
                        await userbot_client(JoinChannelRequest(username))
                        joined_count += 1
                        logger.info(f"Joined channel: {name} ({username})")
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(f"Could not join {name}: {e}")
                if joined_count > 0:
                    logger.info(f"Successfully joined {joined_count} official channels (2FA)")
            except Exception as e:
                logger.error(f"Channel auto-join failed (2FA): {e}")
            
            if plugin_loader:
                plugin_loader.client = userbot_client
                plugin_loader.load_all()
                stats = plugin_loader.get_stats()
                logger.info(f"Reloaded {stats['total']} plugins after 2FA login: {stats['plugins']}")
            else:
                logger.warning("Plugin loader not available - commands may not work")
            
            await event.reply(
                "<b>Login Successful!</b>\n\n"
                "Your session has been created with 2FA.\n"
                "The userbot has been reconnected.\n"
                "You can now use all commands.",
                parse_mode="html"
            )
            logger.info("2FA login successful")
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<b>Error</b>\n\nFailed to verify 2FA: {str(e)}", parse_mode="html")
            logger.error(f"2FA verify error: {e}")

# ============================================
# Remove Command
# ============================================

@bot.on(events.NewMessage(pattern=r"^/remove$", incoming=True, func=lambda e: e.is_private))
async def bot_remove_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply("This command is only for the admin.")
        return
    
    if not ether_db.sessions:
        await event.reply("Database not available.")
        return

    cursor = ether_db.sessions.find({"added_by": event.sender_id})
    buttons = []
    async for doc in cursor:
        name = doc.get("name", "Unknown")
        user_id = doc.get("user_id")
        buttons.append([Button.inline(f"Remove {name} ({user_id})", f"rm_acc:{user_id}")])
    
    # Also check if there's a main session (might not have added_by if migrated)
    main_session = await ether_db.sessions.find_one({"type": "main"})
    if main_session and not any(btn[0].text.endswith(f"({main_session['user_id']})") for btn in buttons):
         buttons.append([Button.inline(f"Remove Main: {main_session.get('name')} ({main_session['user_id']})", f"rm_acc:{main_session['user_id']}")])

    if not buttons:
        await event.reply("<b>No cloned accounts found.</b>", parse_mode="html")
        return

    await event.reply(
        "<b>Account Removal</b>\n\nSelect an account to remove from the system:",
        buttons=buttons,
        parse_mode="html"
    )

@bot.on(events.CallbackQuery(pattern=b"rm_acc:(\\d+)"))
async def cb_remove_account(event):
    if event.sender_id != Config.OWNER_ID:
        await event.answer("Access denied.", alert=True)
        return

    user_id = int(event.pattern_match.group(1).decode())
    
    doc = await ether_db.sessions.find_one({"user_id": user_id})
    if not doc:
        await event.answer("Account not found in database.", alert=True)
        return

    name = doc.get("name", "Unknown")
    
    # 1. Stop the client
    global userbot_client, cloned_clients
    target_client = None

    if user_id in cloned_clients:
        target_client = cloned_clients.pop(user_id)
    elif userbot_client:
        # Check if it's the main client
        try:
            me = await userbot_client.get_me()
            if me and me.id == user_id:
                target_client = userbot_client
                userbot_client = None # Reset main client reference
        except:
            pass

    if target_client:
        try:
            await target_client.disconnect()
        except:
            pass

    # 2. Delete from DB
    await ether_db.sessions.delete_one({"user_id": user_id})

    await event.edit(f"<b>Account Removed:</b> {name} ({user_id})", parse_mode="html", buttons=None)
    logger.info(f"Account removed by admin: {name} ({user_id})")


def set_userbot_client(client, wrapper=None):
    global userbot_client, userbot_wrapper
    userbot_client = client
    userbot_wrapper = wrapper
    logger.info("Userbot client reference set for login")


def set_plugin_loader(loader):
    global plugin_loader
    plugin_loader = loader
    logger.info("Plugin loader reference set for login")

def add_cloned_client(user_id, client):
    global cloned_clients
    cloned_clients[user_id] = client
    logger.info(f"Cloned client added to registry: {user_id}")


# ============================================
# Font Utilities
# ============================================

FONT_MAPS = {
    "1": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"),
    "2": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
    "3": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
    "4": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "5": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"),
    "6": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
    "7": str.maketrans("abcdefghijklmnopqrstuvwxyz", "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"),
    "8": str.maketrans("abcdefghijklmnopqrstuvwxyz", "αв¢∂єƒgнιנкℓмησρզяѕтυνωχуz"),
    "9": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"),
    "10": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"),
}

def apply_font(text, font_key):
    return text.lower().translate(FONT_MAPS[font_key])


# ============================================
# Bot Class
# ============================================

class EtherBot:
    
    def __init__(self):
        self.token = Config.BOT_TOKEN
        self._running = False
        self.me = None
    
    async def fetch_me(self):
        try:
            self.me = await bot.get_me()
            logger.info(f"Bot details fetched: {self.me.first_name} (@{self.me.username})")
            update_dynamic_texts()
        except Exception as e:
            logger.error(f"Failed to fetch bot details: {e}")

    async def start(self) -> None:
        if not Config.BOT_TOKEN:
            logger.warning("No BOT_TOKEN - bot features disabled")
            return
        
        try:
            logger.info(f"Attempting to start bot with token: {self.token[:20]}...")
            logger.info(f"Connecting to Telegram servers...")
            
            # Add timeout to connection
            await asyncio.wait_for(bot.start(bot_token=self.token), timeout=30)
            
            logger.info("Bot connected successfully - fetching details...")
            await self.fetch_me()

            logger.info("Bot ready - waiting for messages...")
            await bot.run_until_disconnected()
        except asyncio.TimeoutError:
            logger.error("Bot connection timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        await bot.disconnect()
        logger.info("Bot stopped")


ether_bot = EtherBot()
