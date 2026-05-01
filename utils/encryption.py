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

import base64
import hashlib
from cryptography.fernet import Fernet
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherEncryption")

def get_fernet() -> Fernet:
    """Generate a Fernet key derived from API_HASH."""
    # Ensure key is 32 bytes and base64 encoded
    key = hashlib.sha256(Config.API_HASH.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_session(session_string: str) -> str:
    """Encrypt a session string."""
    try:
        f = get_fernet()
        return f.encrypt(session_string.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_session(encrypted_session: str) -> str:
    """Decrypt an encrypted session string."""
    try:
        f = get_fernet()
        return f.decrypt(encrypted_session.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise
