from indiek.mockdb.search import build_search_query
import unittest
import re


class TestSearchQuery(unittest.TestCase):
    def test_build_search_query(self):
        raw_str = r'user typed This'
        query = build_search_query(raw_str)
        base_str = '('
        base_str += '|'.join(raw_str.split())
        base_str += ')'
        correct_query = re.compile(base_str, flags=re.IGNORECASE)
        self.assertEqual(correct_query, query)



if __name__ == '__main__':
    unittest.main()