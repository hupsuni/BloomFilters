# Created By Nick Huppert on 4/5/20.

import mmh3
import random
import math


class IBloomLT:
    pass

    _M = 50
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

    def generate_table(self, items, seeds=None, m=None):
        if seeds is None:
            seeds = self.seed_list
        if m is None:
            m = self.m
        bloom = [(0, 0, 0)] * m
        for item in items:
            hash_values = []
            for seed in seeds:
                hash_values.append(mmh3.hash128(str(item).encode(), seed))
            for hash_value in hash_values:
                index = hash_value % m
                id_sum = bloom[index][0] + hash_value
                if bloom[index][1] == 0:
                    hash_sum = hash_value
                else:
                    hash_sum = bloom[index][1] ^ hash_value
                count = bloom[index][2] + 1
                bloom[index] = (id_sum, hash_sum, count)
        return bloom

    def compare_tables(self, table1, table2):
        if len(table1) != len(table2):
            return False
        m = len(table1)
        table1_differences = []
        table2_differences = []
        table3 = [[0, 0, 0]] * m
        # Generate symmetric difference table
        for index in range(m):
            id_sum = table1[index][0] - table2[index][0]
            hash_sum = table1[index][1] ^ table2[index][1]
            count = table1[index][2] - table2[index][2]
            table3[index] = [id_sum, hash_sum, count]
        decodable = True
        while decodable:
            decodable = False
            for index in range(m):
                element = table3[index]
                if element[2] == 1 or element[2] == -1:
                    if element[0] == element[1]:
                        table3 = self.peel_element
                        decodable = True
                        if element[2] == 1:
                            table1_differences.append(element)
                        else:
                            table2_differences.append(element)

        return table1_differences, table2_differences

    def peel_element(self, element, table):
        pass


bloom_table = IBloomLT()
test_data = [
    "test", "test2", "test3", "test4"
]
print(bloom_table.generate_table(test_data))

xor1 = 1 ^ 2 ^ 3 ^ 5
xor2 = 1 ^ 2 ^ 3 ^ 4
xor3 = 5 ^ 4
