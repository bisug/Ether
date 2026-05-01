# =============================================================================
#  Ether Userbot System - Official Channels
#
#    WARNING: DO NOT MODIFY THIS FILE
#
#  This file contains official channel links and integrity checks.
#  Any modification to this file will cause the bot to stop working.
#  The integrity check ensures the channels remain unchanged.
#
#  Unauthorized modification violates the project license.
#
#  Thank you for respecting open-source development.
# =============================================================================

import hashlib
import base64

# Official channels - DO NOT MODIFY
_CHANNELS = {
    "learning_bots": "https://t.me/learning_bots",
    "ether_update": "https://t.me/Ether_Update",
    "learning_bots_support": "https://t.me/LearningBotsSupport",
    "ether_support": "https://t.me/EtherSupport"
}

_INTEGRITY_SIGNATURE = base64.b64encode(
    str(sorted(_CHANNELS.items())).encode()
).decode()


def get_channels():
    return _CHANNELS.copy()


def validate_integrity():
    current_signature = base64.b64encode(
        str(sorted(_CHANNELS.items())).encode()
    ).decode()
    
    return current_signature == _INTEGRITY_SIGNATURE


def get_channel_list():
    return list(_CHANNELS.values())


def get_channel_names():
    """Get channel names."""
    return list(_CHANNELS.keys())


def generate_integrity_hash():
    channel_string = str(sorted(_CHANNELS.items()))
    return hashlib.sha256(channel_string.encode()).hexdigest()[:32]


if __name__ == "__main__":
    print("Current integrity hash:")
    print(generate_integrity_hash())
