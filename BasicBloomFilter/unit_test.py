import unittest
from BasicBloomFilter.bloom_filter import BloomFilter


class TestBloom(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bf = BloomFilter()

    def test_filter_numbers_list(self):
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        list_bloom = self.bf.generate_filter(test_list)
        assert self.bf.verify_item(7, list_bloom) is True
        assert self.bf.verify_item(11, list_bloom) is False

    def test_filter_string_list(self):
        test_list_2 = ["dog", "cat", "elephant"]
        list_bloom_2 = self.bf.generate_filter(test_list_2)
        assert self.bf.verify_item("dog", list_bloom_2) is True
        assert self.bf.verify_item("fly", list_bloom_2) is False

    def test_filter_dictionary(self):
        test_dict = {"dog": "dog",
                     "fly": "cat"}
        dict_bloom = self.bf.generate_filter(test_dict)
        assert self.bf.verify_item({"dog": "dog"}, dict_bloom) is True
        assert self.bf.verify_item({"fly": "cat"}, dict_bloom) is True
        assert self.bf.verify_item({"cat": "fly"}, dict_bloom) is False
