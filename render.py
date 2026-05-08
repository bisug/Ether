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


import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import signal
import sys
import os
from contextlib import suppress

from core.user_client import EtherUserClient
from core.bot import ether_bot, set_userbot_client, set_plugin_loader
from core.loader import PluginLoader
from storage.mongo import ether_db
from config.config import Config
from config.channels import validate_integrity
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger("EtherMain")

plugin_loader = None
shutdown_event = asyncio.Event()


async def keep_alive():
    while not shutdown_event.is_set():
        logger.info("⚡ Ether Alive")
        await asyncio.sleep(300)


async def run_userbot():
    global plugin_loader

    try:
        logger.info("🚀 Starting Userbot")

        db_connected = await ether_db.connect()

        if db_connected:
            logger.info("✅ MongoDB Connected")
        else:
            logger.warning("⚠️ MongoDB Connection Failed")

        session_file = f"{Config.SESSION_NAME}.session"

        if os.path.exists(session_file):
            logger.info(f"✅ Session Found: {session_file}")
        else:
            logger.warning(f"⚠️ Session Missing: {session_file}")

        client_wrapper = EtherUserClient()

        connected = await client_wrapper.connect()

        if not connected:
            logger.error("❌ Failed To Connect User Client")
            return

        logger.info("✅ User Client Connected")

        is_authorized = await client_wrapper.is_authorized()

        if is_authorized:
            logger.info("✅ Userbot Authorized")
        else:
            logger.warning("⚠️ Userbot Not Authorized")
            logger.warning("Use /login")

        client = client_wrapper.get_client()

        set_userbot_client(client, client_wrapper)

        loader = PluginLoader(
            client=client,
            db=ether_db.db,
            owner_id=Config.OWNER_ID
        )

        loader.load_all()

        plugin_loader = loader

        set_plugin_loader(loader)

        stats = loader.get_stats()

        logger.info(f"✅ Plugins Loaded: {stats['total']}")
        logger.info(f"📦 {stats['plugins']}")

        logger.info("🤖 Userbot Running")

        await client.run_until_disconnected()

    except asyncio.CancelledError:
        logger.warning("⚠️ Userbot Cancelled")

    except Exception as e:
        logger.error(f"❌ Userbot Error: {e}", exc_info=True)


async def run_bot():
    try:
        if not Config.BOT_TOKEN:
            logger.warning("⚠️ BOT_TOKEN Missing")
            return

        logger.info("🚀 Starting Bot")

        await ether_bot.start()

        me = await ether_bot.get_me()

        logger.info(f"✅ Bot Started: @{me.username}")

        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.warning("⚠️ Bot Cancelled")

    except Exception as e:
        logger.error(f"❌ Bot Error: {e}", exc_info=True)


async def startup():
    logger.info("════════════════════════════")
    logger.info("🚀 Ether Starting")
    logger.info("════════════════════════════")

    if not validate_integrity():
        logger.error("❌ SECURITY VIOLATION")
        sys.exit(1)

    logger.info("✅ Integrity Validated")

    tasks = [
        asyncio.create_task(run_bot(), name="BotTask"),
        asyncio.create_task(run_userbot(), name="UserbotTask"),
        asyncio.create_task(keep_alive(), name="KeepAliveTask"),
    ]

    logger.info("✅ All Systems Started")

    await shutdown_event.wait()

    logger.warning("⚠️ Shutdown Signal Received")

    for task in tasks:
        task.cancel()

    for task in tasks:
        with suppress(asyncio.CancelledError):
            await task


async def shutdown():
    logger.info("🛑 Shutting Down")

    with suppress(Exception):
        await ether_bot.stop()

    with suppress(Exception):
        await ether_db.close()

    logger.info("✅ Shutdown Complete")


def main():
    global loop

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(
                sig,
                shutdown_event.set
            )

    try:
        loop.run_until_complete(startup())

    except KeyboardInterrupt:
        logger.warning("⚠️ Interrupted")

    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}", exc_info=True)

    finally:
        loop.run_until_complete(shutdown())
        loop.close()


if __name__ == "__main__":
    main()