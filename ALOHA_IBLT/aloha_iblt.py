# Created By Nick Huppert on 4/5/20.
import mmh3
import random
import math
from random import randint, seed


class IBLT:
    """
    Simple implementation of an invertible bloom lookup table.
    The IBLT returned will have the format for a list of lists.
    Each list in an element, each element is of the form [idSum, hashSum, count].
    A list of seed keys is used to seed hash functions for item placement.
    A list of random numbers is used to decide how many times a given item is added to the IBLT.
    """

    _M = 10
    SEED_RANGE = 1000000
    MAX_HASHES = 10
    MAX_RANDOM_HASHES = 1000
    DEFAULT_A_VALUE = 0

    @staticmethod
    def generate_seed_list(seed_key, max_hashes=MAX_HASHES, seed_range=SEED_RANGE):
        """
        List of seeds to be used to derive the item locations.

        Args:
            seed_key: Shared key to instantiate hash functions.
            max_hashes: Upper bound for total hashes to be used.
            seed_range: Range of random numbers to be used to generate a new seed key if not specified.

        Returns:
            list[int]: A list of seed keys which are used to seed hash functions for item placement.
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
    def generate_hash_decider(seed_key, n_value, a_value, length=MAX_RANDOM_HASHES):
        """
        List of random numbers between min and max to decide how many times an item is hashed to locations.

        Args:
            a_value: The value for a in the ALOHA style distribution function.
            seed_key: Shared key to instantiate hash functions.
            n_value: Upper bound for total hashes to be used.
            length: Size of list of random numbers to be generated.

        Returns:
            list[int]: A list of random numbers which decide how many times an item is hashed to be placed into IBLT.
        """
        return Distribution.create_randomly_generated_sequence(length, n_value, a_value, seed_key)

    @staticmethod
    def generate_table(item_ids, seed_key, table_size=_M, max_hashes=MAX_HASHES, a_value=DEFAULT_A_VALUE,
                       hash_decider=None, hash_decider_length=MAX_RANDOM_HASHES, seed_range=MAX_RANDOM_HASHES):
        """
        Generate the randomized hash function quantity based IBLT

        Args:
            a_value: The value for a in the ALOHA style distribution function.
            item_ids: The IDs of the items to be inserted.
            seed_key: Shared key to instantiate hash functions.
            table_size: Size of the IBLT.
            max_hashes: Upper bound for total hashes to be used.
            hash_decider(list[int]): List of random numbers for hashing iterations.
            hash_decider_length: Size of the list of random numbers determining the amount of times an item is added.
            seed_range: The upper bound of the values of any given seed key.

        Returns:
            tuple[list[tuple], list[int], list[int]]: An IBLT as a list of tuples, each element is of the form (idSum, hashSum, count).
        """
        bloom = [(0, 0, 0)] * table_size
        if hash_decider is None:
            hash_decider = IBLT.generate_hash_decider(seed_key, max_hashes, a_value, hash_decider_length)
        seed_list = IBLT.generate_seed_list(seed_key, max_hashes, seed_range)
        for item in item_ids:
            item_hash = mmh3.hash128(str(item).encode(), seed_key)

            hash_quantity = hash_decider[item_hash % len(hash_decider)]
            hash_values = []
            # Calculate hash values for the item and derive the index for encoding
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
    def compare_tables(table1, table2, seed_key, seed_list=None, hash_decider=None,
                       max_hashes=MAX_HASHES, a_value=DEFAULT_A_VALUE, hash_decider_length=MAX_RANDOM_HASHES,
                       seed_range=MAX_RANDOM_HASHES):
        """
        Compares 2 IBLTs and attempts to return the symmetric difference.
        Args:
            a_value: The value for a in the ALOHA style distribution function.
            table1: Invertible bloom filter 1
            table2: Invertible bloom filter 2
            seed_key: Shared key to instantiate hash functions.
            seed_list: List of seed keys for hashing item ids.
            hash_decider(list[int]): List of random numbers for hashing iterations.
            max_hashes: Upper bound for total hashes to be used.
            hash_decider_length: Size of the list of random numbers determining the amount of times an item is added.
            seed_range: The upper bound of the values of any given seed key.

        Returns:
            tuple[list[tuple], list[tuple], str]:
                The symmetric difference of the IBLTs, list 1 is the extra elements from filter 1,
                    list 2 is the extra elements from filter 2, and a string to confirm if the
                    decoding was successful.
        """
        # Check tables are equal size.
        if len(table1) != len(table2):
            return False
        # Generate hash decider or seed list from default values if none are passed in.
        if hash_decider is None:
            hash_decider = IBLT.generate_hash_decider(seed_key, max_hashes, a_value, hash_decider_length)
        if seed_list is None:
            seed_list = IBLT.generate_seed_list(seed_key, max_hashes, seed_range)
        # Create lists for differences and a list to decode.
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
                # Check that the count for an element is 1 or -1.
                if element[2] == 1 or element[2] == -1:
                    # Ensure that the hash of the item ID is equal to the value stored in the table.
                    element_hash = mmh3.hash128(str(element[0]).encode(), seed_key)
                    # If they match, we have a decodable item, now derive which table this element exists
                    # in and remove accordingly.
                    if element_hash == element[1]:
                        table3 = IBLT.peel_element(element[0], seed_key, table3, element[2], seed_list, hash_decider)
                        decodable = True
                        # Add decoded element to appropriate table based on which IBLT it existed in.
                        if element[2] == 1:
                            table1_differences.append(element)
                        else:
                            table2_differences.append(element)
        success = "Success"
        # Scan list to ensure all elements have been decoded.
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
            seed_key: Shared key to instantiate hash functions.
            table(list): The invertible bloom lookup table.
            alteration(int): The indicator as to which list this element was stored in (1 OR -1)
            seed_list: List of seed keys for hashing item ids.
            hash_decider: List of random numbers for hashing iterations.

        Returns:
            list[tuple]:
                An updated invertible bloom lookup table with the given element removed.
        """
        # Get initial hash values of element id.
        item_hash = mmh3.hash128(str(element_id).encode(), seed_key)
        hash_values = []
        # Derive how many times the element has been inserted into the IBLT.
        hash_quantity = hash_decider[item_hash % len(hash_decider)]
        # Generate the list of hashes for the elements positions.
        for i in range(hash_quantity):
            hash_values.append(mmh3.hash128(str(element_id).encode(), seed_list[i]))
        # Remove the element from each index in the table, altering the count field based
        # on the table it came from.
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


class Distribution:

    MAXIMUM_ACCURACY = 10000000

    @staticmethod
    def create_aloha_style_distribution(a, n):
        """
        Creates a probability distribution based off the ALOHA style research methods.

        Args:
            a: The weighting factor of the algorithm.
            n: The size of maximum hashes as a subset of M

        Returns:
            list[int]: A list of weights whose sum is 1.
        """
        distributions = []

        denominator = 0
        for i in range(2, n+1):
            denominator += 1/(i*(i-1)) - (a/2)

        numerator = 0
        for i in range(2, n+1):
            numerator += 1/(i*(i-1)) - a/2
            distributions.append((i, numerator / denominator))

        return distributions

    @staticmethod
    def create_randomly_generated_sequence(size, n_value, a_value, seed_value):
        """
        Creates a sequence of numbers between 2 and N with weightings based on the ALOHA distribution.

        Args:
            size: The length of the list of values.
            n_value: The subset of M where n is the most hash functions.
            a_value: The weighting for the ALOHA distribution.
            seed_value: The seed key used across IBLTs to ensure randomized results are predictable.

        Returns:

        """
        distribution_list = Distribution.create_aloha_style_distribution(a_value, n_value)
        seed(seed_value)
        hash_list = []
        for i in range(0, size):
            random_number = randint(0, Distribution.MAXIMUM_ACCURACY)
            random_number = random_number/Distribution.MAXIMUM_ACCURACY
            for j in range(0, len(distribution_list)):
                if random_number <= distribution_list[j][1]:
                    hash_list.append(distribution_list[j][0])
                    break

        return hash_list


if __name__ == "__main__":
    elements = [1, 2, 3]
    elements2 = [2, 4, 3]
    bloom_full, seed_list1, hash_quantity_list1 = IBLT.generate_table(elements, 5)
    bloom_2, seed_list2, hash_quantity_list2 = IBLT.generate_table(elements2, 5)
    print("Decode::")
    diff = IBLT.compare_tables(bloom_full, bloom_2, 5)
    print(diff)