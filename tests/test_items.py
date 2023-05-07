import unittest
from indiek.mockdb.items import Definition, Theorem, Proof


class TestItemAttr(unittest.TestCase):
    def test_instantiation(self):
        """Test that mockdb Item has the attr specified by indiek-core API."""

        item = Theorem()
        expected_attr = [
            'name',
            'content',
            '_ikid',
            'to_dict'
        ]
        for attr_name in expected_attr:
            self.assertTrue(hasattr(item, attr_name))


class TestItemIO(unittest.TestCase):
    def test_write_read(self):
        item1_dict = {'name': 'item1', 'content': 'blabla'}
        item1 = Definition(**item1_dict)
        item1_dict['_ikid'] = item1.save()

        item2_dict = dict(name='item2', content='nslkdf')
        item2 = Theorem(**item2_dict)
        item2_dict['_ikid'] = item2.save()
        del item1, item2

        item1 = Definition.load(item1_dict['_ikid'])
        self.assertDictEqual(item1.to_dict(), item1_dict)

        item2 = Theorem.load(item2_dict['_ikid'])
        self.assertDictEqual(item2.to_dict(), item2_dict)

    def test_list_all(self):
        item3_dict = {'name': 'item1', 'content': 'blabla'}
        item3 = Proof(**item3_dict)
        item3.save()

        stored = Proof.list_all()
        self.assertIn(item3, stored)

if __name__ == '__main__':
    unittest.main()
