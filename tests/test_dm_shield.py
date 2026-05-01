import unittest
from unittest.mock import MagicMock
from services.dm_shield_service import DMShieldService

class TestDMShieldService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.service = DMShieldService(self.mock_db)

    def test_has_link(self):
        self.assertTrue(self.service.has_link("Check this out: https://google.com"))
        self.assertTrue(self.service.has_link("Join my channel t.me/something"))
        self.assertFalse(self.service.has_link("Just a normal message"))

    def test_has_username(self):
        self.assertTrue(self.service.has_username("Contact @username for info"))
        self.assertFalse(self.service.has_username("No username here"))

    async def test_get_settings_default(self):
        self.mock_db.dm_shield.find_one = MagicMock(return_value=None)

        # Mocking find_one as an async function
        async def mock_find_one(*args, **kwargs):
            return None
        self.mock_db.dm_shield.find_one = mock_find_one

        settings = await self.service.get(12345)
        self.assertFalse(settings["enabled"])

if __name__ == "__main__":
    unittest.main()
