import unittest
from unittest.mock import MagicMock
from services.dm_service import DMService

class TestDMService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.service = DMService(self.mock_db)

    async def test_get_user(self):
        async def mock_find_one(*args, **kwargs):
            return {"user_id": 123}
        self.mock_db["dm_users"].find_one = mock_find_one

        user = await self.service.get_user(123)
        self.assertEqual(user["user_id"], 123)

if __name__ == "__main__":
    unittest.main()
