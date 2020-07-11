# Created By Nick Huppert on 11/7/20.
from datetime import datetime
from time import time
from random import randint
from pympler import asizeof
from IBLT.iblt import IBloomLT
from Random_IBLT.random_iblt import RIBLT


class BloomTest:

    DEFAULT_TEST_SIZE = 1000000
    DEFAULT_TABLE_SIZE = .75
    DEFAULT_TABLE1_DIFFERENCE = .2
    DEFAULT_TABLE2_DIFFERENCE = .2

    @staticmethod
    def test(test_set_size=DEFAULT_TEST_SIZE, table_size=DEFAULT_TABLE_SIZE,
             table1_unique=DEFAULT_TABLE1_DIFFERENCE, table2_unique=DEFAULT_TABLE2_DIFFERENCE):
        test_items1 = []
        test_items2 = []
        start_time = 0
        end_time = 0
        try:
            with open("test_data.txt", "a") as test_data:
                test_data.write("\n%s\n" % datetime.now())
        except (FileNotFoundError, FileExistsError) as error:
            print("%s" % error)
            return

        # Generate test sets
        for i in range(test_set_size):
            test_items1.append(i)
        for i in range(int(test_set_size*table1_unique), int(test_set_size+test_set_size*table2_unique)):
            test_items2.append(i)

        size = int(table_size*test_set_size)
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

        with open("test_data.txt", "a") as test_data:
            test_data.write("IBLT: Data size: %s |Table size: %s |Symmetric difference: %s "
                            "|Table average creation time: %s |Decoding time: %s |Decoding %s \n"
                            % (test_set_size, table_size * test_set_size,
                               test_set_size * (table1_unique + table2_unique),
                               table_creation_time, comparison_time, result[2]))

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

        with open("test_data.txt", "a") as test_data:
            test_data.write("Random Hash IBLT: Data size: %s |Table size: %s |Symmetric difference: %s "
                            "|Table average creation time: %s |Decoding time: %s |Decoding %s \n"
                            % (test_set_size, table_size * test_set_size,
                               test_set_size * (table1_unique + table2_unique),
                               table_creation_time, comparison_time, result[2]))


if __name__ == "__main__":
    for i in range(100):
        BloomTest.test(test_set_size=400000)
