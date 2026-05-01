import unittest
from unittest.mock import MagicMock
from services.shortcut_service import ShortcutService

class TestShortcutService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.service = ShortcutService(self.mock_db)

    async def test_get_shortcut(self):
        async def mock_find_one(*args, **kwargs):
            return {"name": "test"}
        self.mock_db["shortcuts"].find_one = mock_find_one

        shortcut = await self.service.get_shortcut(123, "test")
        self.assertEqual(shortcut["name"], "test")

if __name__ == "__main__":
    unittest.main()
