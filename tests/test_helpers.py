import unittest
from utils.helpers import format_duration, extract_chat_id

class TestHelpers(unittest.TestCase):
    def test_format_duration(self):
        self.assertEqual(format_duration(30), "30s")
        self.assertEqual(format_duration(90), "1m 30s")
        self.assertEqual(format_duration(3661), "1h 1m")

    def test_extract_chat_id(self):
        self.assertEqual(extract_chat_id("@username"), "username")
        self.assertEqual(extract_chat_id("https://t.me/channel"), "channel")
        self.assertEqual(extract_chat_id("just_text"), None)

if __name__ == "__main__":
    unittest.main()
