# Created By Nick Huppert on 4/5/20.
import mmh3
import random


class IBloomLT:
    """
    Simple implementation of an invertible bloom lookup table.
    The IBLT returned will have the format for a list of lists.
    Each list in an element, each element is of the form [idSum, hashSum, count]
    """
    _M = 20
    SEED_RANGE = 1000000
    MAX_HASHES = 13
    MIN_HASHES = 3
    MAX_RANDOM_HASHES = 1000

    def __init__(self, m=_M, max_hashes=MAX_HASHES, seed_list=None, key_hash=None):
        """
        Constructor

        Args:
            m(int): Size of bloom filter array.
            max_hashes(int): Maximum number of unique hashing algorithms to use.
        """
        self.__random_hash_decider = []
        random.seed()
        if seed_list is None:
            self.seed_list = []
            for i in range(max_hashes):
                self.seed_list.append(random.randint(0, self.SEED_RANGE))
        else:
            self.seed_list = seed_list
        self.m = m
        if key_hash is None:
            self.element_hash = random.randint(0, self.SEED_RANGE)
        else:
            self.element_hash = key_hash
        random.seed(key_hash)
        # Generate the key count list to be used for deciding how many times an element should be hashed in the table.
        for i in range(self.MAX_RANDOM_HASHES):
            self.__random_hash_decider.append(random.randint(self.MIN_HASHES, self.MAX_HASHES + 1))

# TODO - Alter to use random hash quantities
    def generate_table(self, item_ids):
        """
        Given a list of item IDs, generate a corresponding IBLT
        Args:
            item_ids(list): A list of IDs for items to be included in IBLT.

        Returns:
            list: An invertible bloom lookup table in format list of lists.
        """
        bloom = [(0, 0, 0)] * self.m
        for item in item_ids:
            hash_values = []
            for seed in self.seed_list:
                hash_values.append(mmh3.hash128(str(item).encode(), seed))
            for hash_value in hash_values:
                index = hash_value % self.m
                id_sum = bloom[index][0] ^ item
                if bloom[index][1] == 0:
                    hash_sum = mmh3.hash128(str(item).encode(), self.element_hash)
                else:
                    hash_sum = bloom[index][1] ^ mmh3.hash128(str(item).encode(), self.element_hash)
                count = bloom[index][2] + 1
                bloom[index] = (id_sum, hash_sum, count)
        return bloom

    def compare_tables(self, table1, table2):
        """
        Compares 2 IBLTs and attempts to return the symmetric difference.
        Args:
            table1: Invertible bloom filter 1
            table2: Invertible bloom filter 1

        Returns:
            list list str:
                The symmetric difference of the IBLTs, list 1 is the extra elements from filter 1,
                    list 2 is the extra elements from filter 2, and a string to confirm if the
                    decoding was successful.
        """
        if len(table1) != len(table2):
            return False
        m = len(table1)
        table1_differences = []
        table2_differences = []
        table3 = [[0, 0, 0]] * m
        # Generate symmetric difference table
        for index in range(m):
            id_sum = table1[index][0] ^ table2[index][0]
            hash_sum = table1[index][1] ^ table2[index][1]
            count = table1[index][2] - table2[index][2]
            table3[index] = [id_sum, hash_sum, count]
        decodable = True
        while decodable is True:
            decodable = False
            for index in range(m):
                quick_check_pass = False
                element = table3[index]
                if element[2] == 1 or element[2] == -1:
                    element_hash = mmh3.hash128(str(element[0]).encode(), self.element_hash)
                    if element_hash == element[1]:
                        table3 = self.peel_element(element[0], table3, element[2])
                        decodable = True
                        if element[2] == 1:
                            table1_differences.append(element)
                        else:
                            table2_differences.append(element)
        success = "Success"
        for index in range(m):
            if table3[index][1] != 0:
                success = "Failed"
        return table1_differences, table2_differences, success

    def peel_element(self, element_id, table, alteration):
        """
        Peels a single element from a given IBLT.
        
        Args:
            element_id(int): The element to be peeled.
            table(list): The invertible bloom lookup table.
            alteration(int): The indicator as to which list this element was stored in (1 OR -1)

        Returns:
            list:
                An updated invertible bloom lookup table with the given element removed.
        """
        hash_values = []
        element_hash = mmh3.hash128(str(element_id).encode(), self.element_hash)
        for seed in self.seed_list:
            hash_values.append(mmh3.hash128(str(element_id).encode(), seed))
        for hash_value in hash_values:
            index = hash_value % self.m
            id_sum = table[index][0] ^ element_id
            if table[index][1] == 0:
                hash_sum = element_hash
            else:
                hash_sum = table[index][1] ^ element_hash
            count = table[index][2] - alteration
            table[index] = (id_sum, hash_sum, count)
        return table


if __name__ == "__main__":
    bloom_table = IBloomLT()
    test_data = [
        5, 9, 3245, 7653, 124, 8764, 2314, 7452, 234, 7453, 234, 56437, 1
    ]
    test_data2 = [
        5, 9, 3245, 7653, 124, 8764, 2314, 7452, 234, 7453, 234, 56437, 2, 6
    ]
    bloom_table1 = bloom_table.generate_table(test_data)
    bloom_table2 = bloom_table.generate_table(test_data2)

    extra1, extra2, lookup_success = (bloom_table.compare_tables(bloom_table1, bloom_table2))
    print("Table 1 contains extra elements: " + str(extra1))
    print("Table 2 contains extra elements: " + str(extra2))
    print(lookup_success)
