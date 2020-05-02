import mmh3
import random
import math


class BloomFilter:
    """
    Bloom Filter class, creates and verifies bloom filters for items.
    """
    _M = 500
    _K = 9
    SEED_RANGE = 1000000

    def __init__(self, m=_M, k=_K):
        """
        Constructor

        Args:
            m(int): Size of bloom filter array.
            k(int): Number of unique hashing algorithms to use.
        """
        random.seed()
        self.seed_list = []
        for i in range(k):
            self.seed_list.append(random.randint(0, self.SEED_RANGE))
        self.m = m

    def generate_filter(self, items, seeds=None, n=None):
        """
        Given a number of items, generate a bloom filter.

        Args:
            items(list, dict): A list of items or a single item to be inserted to the filter.
            seeds(list): (Optional) A list of seed values for hashing algorithm.
            n(int): (Optional) Size of bloom filter array.

        Returns:
            bytearray: An array of binary bits representing the bloom filter.

        """
        if type(items) == dict:
            keys = items.keys()
            temp_list = []
            for key in keys:
                temp_string = str(key) + ":" + str(items[key])
                temp_list.append(temp_string)
            items = temp_list
        bloom_filter = bytearray(int(self.m))
        if seeds is None:
            seeds = self.seed_list
        if n is None:
            n = self.m
        for item in items:
            for seed in seeds:
                index = mmh3.hash128(str(item).encode(), seed) % n
                bloom_filter[index] = 1
        return bloom_filter

    def verify_item(self, item, bloom_filter, seeds=None, n=None):
        """
        Verifies if an item is present in the supplied bloom filter.

        Args:
            item: The item to be checked.
            bloom_filter(bytearray): The array of binary values representing the bloom filter
            seeds(list): A list of k seeds for the hashing algorithm.
            n(int): (Optional) Size of bloom filter array.

        Returns:
            bool: If the item may be in the bloom filter or not.
        """
        verify_item = None
        if seeds is None:
            seeds = self.seed_list
        if n is None:
            n = self.m
        print(type(item))
        if type(item) == dict:
            if len(item) != 1:
                return False
            keys = item.keys()
            for key in keys:
                verify_item = str(key) + ":" + str(item[key])
        else:
            verify_item = item
        verify = True
        try:
            for seed in seeds:
                index = mmh3.hash128(str(verify_item).encode(), seed) % n
                if bloom_filter[index] == 0:
                    verify = False
                    break
        except IndexError:
            verify = False
        finally:
            return verify

    @staticmethod
    def calculate_ideal_filter_size_m(expected_quantity_of_elements, desired_false_positive_rate):
        """
        Calculates the ideal bloom filter size based on expected elements to be inserted
        and desired false positive rate.

        Args:
            expected_quantity_of_elements(int): The number of elements expected to be used in one bloom filter.
            desired_false_positive_rate(float): The desired false positive rate (f) for the filter. 1 >= f >= 0.

        Returns:
            int: The optimal size (m) of the bloom filter.
        """
        numerator = abs(math.log(desired_false_positive_rate))
        denominator = math.pow(math.log(2), 2)
        size = expected_quantity_of_elements * numerator / denominator
        return int(math.ceil(size))

    @staticmethod
    def calculate_ideal_hash_quantity_k(array_size, element_quantity):
        """
        Calculates the ideal number of hash functions for a bloom filter.

        Args:
            array_size(int): The size (m) of the bloom filter.
            element_quantity(int): The expected quantity of elements inserted into the filter.

        Returns:
            int: The ideal number of hash functions (k) for filter.
        """
        quantity = (array_size / element_quantity) * math.log(2)
        return int(round(quantity))

    @staticmethod
    def calculate_approximate_false_positive_rate(array_size, element_quantity, number_of_hashes):
        """
        Calculates the approximate false positive rate for a given bloom filter.

        Args:
            array_size(int): Size (m) of the bloom filter.
            element_quantity(int): The quantity (n) of elements in bloom filter.
            number_of_hashes(int): The number of hash functions (k).

        Returns:
            float: The probability of false positives (f) for given values. 1 >= f >= 0.
        """
        return (1 - (1 - (number_of_hashes/array_size)) ** element_quantity) ** number_of_hashes

    @staticmethod
    def calculate_desired_filter_values(expected_number_of_elements, desired_false_positive_rate):
        """
        Given an expected number of elements to be inserted into the bloom filter and a desired false positive rate,
        calculate the optimal size of the filter and number of hash functions.

        Args:
            expected_number_of_elements(int): The number of elements expected to be used in one bloom filter.
            desired_false_positive_rate(float): The desired false positive rate (f) for the filter. 1 >= f >= 0.

        Returns:
            dict: A dictionary of ideal values for bloom filters size (m) and hash functions (k).
        """
        m = BloomFilter.calculate_ideal_filter_size_m(expected_number_of_elements, desired_false_positive_rate)
        k = BloomFilter.calculate_ideal_hash_quantity_k(m, expected_number_of_elements)
        return {"k": k, "m": m}
