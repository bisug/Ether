import unittest
from unittest.mock import MagicMock
from core.loader import PluginLoader
from pathlib import Path

class TestPluginLoader(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.loader = PluginLoader(self.mock_client, self.mock_db, owner_id=123)

    def test_get_stats(self):
        self.loader.loaded = ["ping", "alive"]
        stats = self.loader.get_stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["plugins"], ["ping", "alive"])

if __name__ == "__main__":
    unittest.main()
