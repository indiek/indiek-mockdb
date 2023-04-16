import unittest
from indiek.mockdb.items import Item


class TestItemAttr(unittest.TestCase):
    def test_instantiation(self):
        item = Item()
        expected_attr = [
            'name',
            'content',
        ]
        for attr_name in expected_attr:
            self.assertTrue(hasattr(item, attr_name))


if __name__ == '__main__':
    unittest.main()
