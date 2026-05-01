import os
import sys
from unittest.mock import MagicMock

# Set required environment variables for tests
os.environ['API_ID'] = '12345'
os.environ['API_HASH'] = 'abcdef'
os.environ['OWNER_ID'] = '67890'
os.environ['BOT_TOKEN'] = 'token'
os.environ['MONGO_URI'] = 'mongodb://localhost:27017'

# Mock Telethon and other dependencies before importing core modules
sys.modules['telethon'] = MagicMock()
sys.modules['telethon.events'] = MagicMock()
sys.modules['motor'] = MagicMock()
sys.modules['motor.motor_asyncio'] = MagicMock()
sys.modules['motor.motor_asyncio'].AsyncIOMotorClient = MagicMock()
