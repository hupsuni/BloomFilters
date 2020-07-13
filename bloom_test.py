# Created By Nick Huppert on 11/7/20.
from datetime import datetime
from time import time
from random import randint
from pympler import asizeof
from IBLT.iblt import IBloomLT
from Random_IBLT.random_iblt import RIBLT


class BloomTest:

    DEFAULT_TEST_SIZE = 1000000
    DEFAULT_TABLE_SIZE = .6
    DEFAULT_SYMMETRIC_DIFFERENCE = .4

    @staticmethod
    def test(test_items1, test_items2, symmetric_difference, table_size=DEFAULT_TABLE_SIZE):

        if len(test_items1) != len(test_items2):
            return

        test_set_size = len(test_items1)
        size = int(test_set_size * table_size)
        bloom_table = IBloomLT(m=size)

        # Test standard IBLT
        start_time = time()
        bloom1 = bloom_table.generate_table(test_items1)
        end_time = time()
        table_creation_time = end_time - start_time
        start_time = time()
        bloom2 = bloom_table.generate_table(test_items2)
        end_time = time()
        table_creation_time = (end_time - start_time + table_creation_time) / 2
        start_time = time()
        result = bloom_table.compare_tables(bloom1, bloom2)
        end_time = time()
        comparison_time = end_time - start_time
        print(result[2])
        average_table_size = (asizeof.asizeof(bloom1) + asizeof.asizeof(bloom2)) / 2

        BloomTest.write_to_file("Normal IBLT", test_set_size, table_size, symmetric_difference,
                                average_table_size, table_creation_time, comparison_time, result[2])
        # Test Random IBLT
        key = randint(1, 1000)
        start_time = time()
        bloom1, x, y = RIBLT.generate_table(test_items1, seed_key=key, table_size=size)
        end_time = time()
        table_creation_time = end_time - start_time
        start_time = time()
        bloom2, a, b = RIBLT.generate_table(test_items2, seed_key=key, table_size=size)
        end_time = time()
        table_creation_time = (end_time - start_time + table_creation_time) / 2
        start_time = time()
        result = RIBLT.compare_tables(bloom1, bloom2, key)
        end_time = time()
        comparison_time = end_time - start_time
        print(result[2])
        average_table_size = (asizeof.asizeof(bloom1) + asizeof.asizeof(bloom2)) / 2
        BloomTest.write_to_file("Random IBLT", test_set_size, table_size, symmetric_difference,
                                average_table_size, table_creation_time, comparison_time, result[2])

    @staticmethod
    def generate_test_set(size=DEFAULT_TEST_SIZE, symmetric_difference=DEFAULT_SYMMETRIC_DIFFERENCE):
        test_items1 = []
        test_items2 = []
        for i in range(size):
            test_items1.append(i)
        for i in range(int(size * (symmetric_difference / 2)),
                       int(size + size * (symmetric_difference / 2))):
            test_items2.append(i)

        return test_items1, test_items2

    @staticmethod
    def write_to_file(test_type, test_set_size, table_size, symmetric_difference, average_table_size,
                      table_creation_time, comparison_time, result):
        with open("test_data.txt", "a") as test_data:
            test_data.write("%s: Data size: %s |Table size: %s |Symmetric difference: %s "
                            "|Table average creation time: %s |Average table byte size: %s "
                            "|Decoding time: %s |Decoding %s \n"
                            % (test_type, test_set_size, table_size * test_set_size,
                               symmetric_difference, average_table_size,
                               table_creation_time, comparison_time, result))


if __name__ == "__main__":
    difference = .3
    reps = 5
    set_size = 100000
    test_data1, test_data2 = BloomTest.generate_test_set(set_size, difference)

    # Test table sizes from 45% to 60%
    with open("test_data.txt", "a") as test_data:
        test_data.write("Testing table sizes on static symmetric difference\n")
    for i in range(45, 60):
        for j in range(reps):
            BloomTest.test(test_data1, test_data2, symmetric_difference=difference, table_size=i/100)

    # Test symmetric differences from 25% to 50% on static size
    with open("test_data.txt", "a") as test_data:
        test_data.write("Testing symmetric difference on static table size\n")
    for i in range(25, 45):
        test_data1, test_data2 = BloomTest.generate_test_set(set_size, i/100)
        for j in range(reps):
            BloomTest.test(test_data1, test_data2, symmetric_difference=i/100, table_size=.6)
