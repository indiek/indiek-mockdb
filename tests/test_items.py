import unittest
from indiek.mockdb.items import (Definition, 
                                 Theorem, 
                                 Proof, 
                                 ITEM_CLASSES, 
                                 MixedTypeOverrideError,
                                 Note)
import re


class TestItemAPI(unittest.TestCase):
    def test_instantiation(self):
        """Test that mockdb Item has the attr specified by indiek-core API."""

        item = Theorem()
        expected_attr = [
            'name',
            'content',
            'ikid',
            'to_dict'
        ]
        for attr_name in expected_attr:
            self.assertTrue(hasattr(item, attr_name))


    def test_comparison(self):
        definition = Definition()
        tmp_prf1, tmp_prf2 = Proof(), Proof()

        # before saving similar content is equiv
        self.assertEqual(tmp_prf1, tmp_prf2)

        # different types are not
        self.assertNotEqual(definition, tmp_prf2)

        id1 = definition.save()
        # breakpoint()
        self.assertRaises(AssertionError, Definition, ikid=id1)

        # because of the type, definition not equal to tmp_prf1
        self.assertNotEqual(tmp_prf1, definition)

        # and now definition should have been deleted
        self.assertNotIn(id1, Definition._item_dict.keys())


class TestItemIO(unittest.TestCase):
    def test_write_read(self):
        item1_dict = {'name': 'item1', 'content': 'blabla'}
        item1 = Definition(**item1_dict)
        item1_dict['ikid'] = item1.save()

        item2_dict = dict(name='item2', content='nslkdf')
        item2 = Theorem(**item2_dict)
        item2_dict['ikid'] = item2.save()
        del item1, item2

        item1 = Definition.load(item1_dict['ikid'])
        self.assertEqual(item1.load_note('name').str, item1_dict['name'])
        self.assertEqual(item1.load_note('content').str, item1_dict['content'])
        self.assertEqual(item1.ikid, item1_dict['ikid'])

        item2 = Theorem.load(item2_dict['ikid'])
        self.assertEqual(item2.load_note('name').str, item2_dict['name'])
        self.assertEqual(item2.load_note('content').str, item2_dict['content'])
        self.assertEqual(item2.ikid, item2_dict['ikid'])

    def test_reload(self):
        item = Definition(name='blabla')
        item.save()
        item.name='fake'
        item.reload()
        self.assertEqual(item.load_note('name').str, 'blabla')

    def test_more_io(self):
        definition = Definition()
        tmp_prf1 = Proof()
        ikid = definition.save()
        
        # overriding ID assigned to definition with a proof throws error
        tmp_prf1.ikid = ikid
        self.assertRaises(MixedTypeOverrideError, tmp_prf1.save)

        # but after deleting the saved one it will work
        # breakpoint()
        definition.delete()
        tmp_prf1.save()
        proof_name = tmp_prf1.load_note('name')
        self.assertEqual(proof_name.str, '')

        # edit name
        proof_name.flat_content =["tournam"]
        proof_name.save()
        tmp_prf1.save()  # TODO: saving propagates?
        # breakpoint()
        self.assertEqual(tmp_prf1.load_note('name').str, 'tournam')
        self.assertEqual(tmp_prf1.ikid, ikid)


class TestSearch(unittest.TestCase):
    def test_list_all(self):
        item3_dict = {'name': 'item1', 'content': 'blabla'}
        item3 = Proof(**item3_dict)
        item3.save()

        stored = Proof.list_all()
        self.assertIn(item3, stored)

    def test_str_filter(self):
        bambi = 'bambi'
        nany = 'nany'
        bamb = 'bamb'
        for cls in ITEM_CLASSES:
            # write two items with specific str
            name_str = cls.__name__ + ' bambi'
            content_str = cls.__name__ + ' nany'
            item = cls(name=name_str, content=content_str)
            item.save()

            name_str = cls.__name__ + ' bamboo'
            content_str = cls.__name__ + ' granny'
            item2 = cls(name=name_str, content=content_str)
            item2.save()
        
            # check correct counts returned
            # breakpoint()
            with_bambi = len(cls.str_filter(bambi))
            self.assertEqual(with_bambi, 1)
            with_nany = len(cls.str_filter(nany))
            self.assertEqual(with_nany, 1)
            with_bamb = len(cls.str_filter(bamb))
            self.assertEqual(with_bamb, 2)


if __name__ == '__main__':
    unittest.main()
