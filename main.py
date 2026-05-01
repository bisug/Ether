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

import asyncio
import sys
import os

from telethon.sessions import StringSession
from core.user_client import EtherUserClient
from utils.encryption import encrypt_session, decrypt_session
from core.buttons import ether_bot, set_userbot_client, set_plugin_loader, add_cloned_client
from core.loader import PluginLoader
from storage.mongo import ether_db
from config.config import Config
from config.channels import validate_integrity
from utils.logger import setup_logger, get_logger

logger = get_logger("EtherMain")

# Global loader for plugin reloading after login
plugin_loader = None


async def run_userbot():

    # Connect to database
    db_connected = await ether_db.connect()
    if not db_connected:
        logger.warning("Running without database - some features disabled")
    
    # Initialize main Telegram client
    client_wrapper = EtherUserClient()
    logger.info("Initializing main Telegram client...")
    
    # Session Migration and loading
    session_file = f"{Config.SESSION_NAME}.session"
    if os.path.exists(session_file):
        logger.info("Local session file found. Migrating to MongoDB...")
        try:
            connected = await client_wrapper.connect()
            if connected and await client_wrapper.is_authorized():
                # Get string session to store in DB
                session_str = StringSession.save(client_wrapper.client.session)
                encrypted = encrypt_session(session_str)
                me = await client_wrapper.client.get_me()

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
                    logger.info(f"Main session migrated to MongoDB for {me.first_name}")

                    # Disconnect and delete local session
                    await client_wrapper.disconnect()
                    await asyncio.sleep(1)

                    to_delete = [
                        session_file,
                        f"{session_file}-journal",
                        f"{session_file}-wal",
                        f"{session_file}-shm"
                    ]
                    for f in to_delete:
                        if os.path.exists(f):
                            os.remove(f)
                    logger.info("Local session files deleted after migration")
                else:
                    logger.warning("Database not available for migration")
            else:
                logger.warning("Local session not authorized, skipping migration")
        except Exception as e:
            logger.error(f"Migration error: {e}")

    # Load all sessions from MongoDB
    clients_to_run = []
    main_client = None

    if db_connected and ether_db.sessions:
        cursor = ether_db.sessions.find({})
        async for session_doc in cursor:
            try:
                encrypted_str = session_doc["session"]
                decrypted_str = decrypt_session(encrypted_str)

                client = client_wrapper.create_string_client(decrypted_str)
                connected = await client_wrapper.connect(client)

                if connected and await client_wrapper.is_authorized(client):
                    if session_doc.get("type") == "main":
                        main_client = client
                        logger.info(f"Main session loaded from MongoDB: {session_doc.get('name')}")
                    else:
                        clients_to_run.append(client)
                        add_cloned_client(session_doc["user_id"], client)
                        logger.info(f"Cloned session loaded from MongoDB: {session_doc.get('name')}")
                else:
                    logger.warning(f"Session for {session_doc.get('name')} failed to authorize")
            except Exception as e:
                logger.error(f"Error loading session from DB: {e}")

    # Fallback to default if no main session in DB
    if not main_client:
        logger.info("No main session found in DB, using default initialization")
        connected = await client_wrapper.connect()
        main_client = client_wrapper.get_client()

        is_authorized = await client_wrapper.is_authorized()
        if not is_authorized:
            logger.warning("Main session not authorized. Use /login to authenticate.")
        else:
            logger.info("Main userbot session authorized")

    # Set userbot client reference for bot login UI
    set_userbot_client(main_client, client_wrapper)
    
    # Load all plugins for ALL clients
    global plugin_loader
    loader = PluginLoader(
        client=main_client,
        db=ether_db.db,
        owner_id=Config.OWNER_ID
    )

    # Load for main client
    loader.load_all()
    
    # Load for all cloned clients
    for client in clients_to_run:
        loader.load_all(client)

    plugin_loader = loader
    set_plugin_loader(loader)
    
    stats = loader.get_stats()
    logger.info(f"Total {len(clients_to_run) + 1} clients active")
    logger.info(f"Loaded {stats['total']} plugins across all clients")

    # Run all clients
    tasks = [main_client.run_until_disconnected()]
    for client in clients_to_run:
        tasks.append(client.run_until_disconnected())
    
    await asyncio.gather(*tasks)


async def run_bot():
    if not Config.BOT_TOKEN:
        logger.info("No BOT_TOKEN - bot UI disabled")
        return
    
    logger.info("Bot Ui starting...")
    await ether_bot.start()


async def startup():
    setup_logger()
    logger.info("=" * 50)
    logger.info("Ether Hybrid System Starting")
    logger.info("=" * 50)
    
    # Validate channels file integrity
    if not validate_integrity():
        logger.error("=" * 50)
        logger.error("SECURITY VIOLATION DETECTED")
        logger.error("The channels.py file has been modified.")
        logger.error("Unauthorized modification detected.")
        logger.error("Bot will not start to protect integrity.")
        logger.error("=" * 50)
        print("\n" + "=" * 50)
        print("SECURITY VIOLATION DETECTED")
        print("The channels.py file has been modified.")
        print("Unauthorized modification detected.")
        print("Bot will not start to protect integrity.")
        print("=" * 50 + "\n")
        sys.exit(1)
    
    logger.info("Channels file integrity validated successfully")
    
    # Start bot first - it should always run for /login
    bot_task = asyncio.create_task(run_bot())
    
    # Start userbot in background - may fail if session is invalid
    userbot_task = asyncio.create_task(run_userbot())
    
    # Wait for bot to finish (it should run indefinitely)
    try:
        await bot_task
    except Exception as e:
        logger.error(f"Bot task failed: {e}", exc_info=True)
    finally:
        # Cancel userbot if bot stops
        if not userbot_task.done():
            userbot_task.cancel()
            try:
                await userbot_task
            except asyncio.CancelledError:
                pass


async def shutdown():
    logger.info("Shutting down...")
    await ether_bot.stop()
    await ether_db.close()


def main():
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        try:
            asyncio.run(shutdown())
        except Exception:
            pass


if __name__ == "__main__":
    main()