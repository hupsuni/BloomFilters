# Created By Nick Huppert on 4/5/20.
import mmh3
import random


class RIBLT:
    """
    Simple implementation of an invertible bloom lookup table.
    The IBLT returned will have the format for a list of lists.
    Each list in an element, each element is of the form [idSum, hashSum, count]
    """

    _M = 10
    SEED_RANGE = 1000000
    MAX_HASHES = 13
    MIN_HASHES = 3
    MAX_RANDOM_HASHES = 1000

    @staticmethod
    def generate_seed_list(seed_key, max_hashes=MAX_HASHES, seed_range=SEED_RANGE):
        """
        List of seeds to be used to derive the item locations.

        Args:
            seed_key:
            max_hashes:
            seed_range:

        Returns:

        """
        random.seed(seed_key)
        seed_list = []
        i = 0
        while i < max_hashes:
            chosen_seed = random.randint(0, seed_range)
            if chosen_seed not in seed_list:
                seed_list.append(chosen_seed)
                i += 1
        return seed_list

    @staticmethod
    def generate_hash_decider(seed_key, min_hashes=MIN_HASHES, max_hashes=MAX_HASHES, length=MAX_RANDOM_HASHES):
        """
        List of random numbers between min and max to decide how many times an item is hashed to locations.

        Args:
            seed_key:
            min_hashes:
            max_hashes:
            length:

        Returns:

        """
        random.seed(seed_key)
        hash_decider = []
        for i in range(length):
            hash_decider.append(random.randint(min_hashes, max_hashes))
        return hash_decider

    @staticmethod
    def generate_table(item_ids, seed_key, table_size=_M, min_hashes=MIN_HASHES,
                       max_hashes=MAX_HASHES, hash_decider_length=MAX_RANDOM_HASHES, seed_range=MAX_RANDOM_HASHES):
        """
        Generate the randomized hash function quantity based IBLT

        Args:
            item_ids:
            seed_key:
            table_size:
            min_hashes:
            max_hashes:
            hash_decider_length:
            seed_range:

        Returns:

        """
        bloom = [(0, 0, 0)] * table_size
        hash_decider = RIBLT.generate_hash_decider(seed_key, min_hashes, max_hashes, hash_decider_length)
        seed_list = RIBLT.generate_seed_list(seed_key, max_hashes, seed_range)
        for item in item_ids:
            item_hash = mmh3.hash128(str(item).encode(), seed_key)

            hash_quantity = hash_decider[item_hash % len(hash_decider)]
            hash_values = []
            print(str(item) + ":" + str(hash_quantity))
            # TODO - Make better choices about which algo to use.
            for i in range(hash_quantity):
                hash_values.append(mmh3.hash128(str(item).encode(), seed_list[i]))
            for hash_value in hash_values:
                index = hash_value % table_size
                id_sum = bloom[index][0] ^ item
                if bloom[index][1] == 0:
                    hash_sum = item_hash
                else:
                    hash_sum = bloom[index][1] ^ item_hash
                count = bloom[index][2] + 1
                bloom[index] = (id_sum, hash_sum, count)
        return bloom, seed_list, hash_decider

    @staticmethod
    def compare_tables(table1, table2, seed_key, seed_list=None, hash_decider=None, min_hashes=MIN_HASHES,
                       max_hashes=MAX_HASHES, hash_decider_length=MAX_RANDOM_HASHES,
                       seed_range=MAX_RANDOM_HASHES):
        """
        Compares 2 IBLTs and attempts to return the symmetric difference.
        Args:
            table1: Invertible bloom filter 1
            table2: Invertible bloom filter 2
            seed_key:
            seed_list:
            hash_decider:
            min_hashes:
            max_hashes:
            hash_decider_length:
            seed_range:

        Returns:
            list list str:
                The symmetric difference of the IBLTs, list 1 is the extra elements from filter 1,
                    list 2 is the extra elements from filter 2, and a string to confirm if the
                    decoding was successful.
        """
        if len(table1) != len(table2):
            return False
        if hash_decider is None:
            hash_decider = RIBLT.generate_hash_decider(seed_key, min_hashes, max_hashes, hash_decider_length)
        if seed_list is None:
            seed_list = RIBLT.generate_seed_list(seed_key, max_hashes, seed_range)
        print(table1)
        table_size = len(table1)
        table1_differences = []
        table2_differences = []
        table3 = [[0, 0, 0]] * table_size
        # Generate symmetric difference table
        for index in range(table_size):
            id_sum = table1[index][0] ^ table2[index][0]
            hash_sum = table1[index][1] ^ table2[index][1]
            count = table1[index][2] - table2[index][2]
            table3[index] = [id_sum, hash_sum, count]
        # Begin decoding table
        decodable = True
        while decodable is True:
            decodable = False
            for index in range(table_size):
                element = table3[index]
                if element[2] == 1 or element[2] == -1:
                    element_hash = mmh3.hash128(str(element[0]).encode(), seed_key)
                    if element_hash == element[1]:
                        table3 = RIBLT.peel_element(element[0], seed_key, table3, element[2], seed_list, hash_decider)
                        decodable = True
                        if element[2] == 1:
                            table1_differences.append(element)
                        else:
                            table2_differences.append(element)
        success = "Success"
        for index in range(table_size):
            if table3[index][1] != 0:
                success = "Failed"
        return table1_differences, table2_differences, success

    @staticmethod
    def peel_element(element_id, seed_key, table, alteration, seed_list, hash_decider):
        """
        Peels a single element from a given IBLT.
        
        Args:
            element_id(int): The element to be peeled.
            seed_key:
            table(list): The invertible bloom lookup table.
            alteration(int): The indicator as to which list this element was stored in (1 OR -1)
            seed_list:
            hash_decider:

        Returns:
            list:
                An updated invertible bloom lookup table with the given element removed.
        """
        item_hash = mmh3.hash128(str(element_id).encode(), seed_key)
        hash_values = []
        hash_quantity = hash_decider[item_hash % len(hash_decider)]
        print(str(element_id) + ":" + str(hash_quantity))
        # TODO - Make better choices about which algo to use.
        for i in range(hash_quantity):
            hash_values.append(mmh3.hash128(str(element_id).encode(), seed_list[i]))
        for hash_value in hash_values:
            index = hash_value % len(table)
            id_sum = table[index][0] ^ element_id
            if table[index][1] == 0:
                hash_sum = item_hash
            else:
                hash_sum = table[index][1] ^ item_hash
            count = table[index][2] - alteration
            table[index] = (id_sum, hash_sum, count)
        return table


if __name__ == "__main__":
    elements = [1, 2, 3]
    elements2 = [2, 4, 3]
    bloom_full, seed_list1, hash_quantity_list1 = RIBLT.generate_table(elements, 5)
    bloom_2, seed_list2, hash_quantity_list2 = RIBLT.generate_table(elements2, 5)
    print("Decode::")
    diff = RIBLT.compare_tables(bloom_full, bloom_2, 5)
    print(diff)
