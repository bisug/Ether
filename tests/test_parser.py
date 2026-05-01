import unittest
from utils.parser import parse_links, escape_html

class TestParser(unittest.TestCase):
    def test_escape_html(self):
        self.assertEqual(escape_html("Hello <world> & \"everyone\""), "Hello &lt;world&gt; &amp; &quot;everyone&quot;")

    def test_parse_links(self):
        text = "Google -> https://google.com\nNormal text"
        expected = '<a href="https://google.com">Google</a>\nNormal text'
        self.assertEqual(parse_links(text), expected)

if __name__ == "__main__":
    unittest.main()
