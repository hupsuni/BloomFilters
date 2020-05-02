import mmh3
import random


class BloomFilter:
    """
    Bloom Filter class, creates and verifies bloom filters for items.
    """
    _N = 500
    _K = 9
    SEED_RANGE = 1000000

    def __init__(self, n=_N, k=_K):
        """
        Constructor

        Args:
            n(int): Size of bloom filter array.
            k(int): Number of unique hashing algorithms to use.
        """
        random.seed()
        self.seed_list = []
        for i in range(k):
            self.seed_list.append(random.randint(0, self.SEED_RANGE))
        self.n = n

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
        bloom_filter = bytearray(int(self.n))
        if seeds is None:
            seeds = self.seed_list
        if n is None:
            n = self.n
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
            n = self.n
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
