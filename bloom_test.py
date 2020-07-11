# Created By Nick Huppert on 11/7/20.
from datetime import datetime
from random import randint
from pympler import asizeof
from IBLT.iblt import IBloomLT
from Random_IBLT.random_iblt import RIBLT


class BloomTest:

    DEFAULT_TEST_SIZE = 1000000
    DEFAULT_TABLE_SIZE = .8
    DEFAULT_TABLE1_DIFFERENCE = .2
    DEFAULT_TABLE2_DIFFERENCE = .3

    @staticmethod
    def test(test_set_size=DEFAULT_TEST_SIZE, table_size=DEFAULT_TABLE_SIZE,
             table1_unique=DEFAULT_TABLE1_DIFFERENCE, table2_unique=DEFAULT_TABLE2_DIFFERENCE):
        test_items1 = []
        test_items2 = []
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
        bloom1 = bloom_table.generate_table(test_items1)
        bloom2 = bloom_table.generate_table(test_items2)
        print(bloom_table.compare_tables(bloom1, bloom2)[2])
        print(asizeof.asizeof(bloom1))
        print(asizeof.asizeof(bloom2))

        # Test Random IBLT
        key = randint(1, 1000)
        bloom1, x, y = RIBLT.generate_table(test_items1, seed_key=key, table_size=size)
        bloom2, a, b = RIBLT.generate_table(test_items2, seed_key=key, table_size=size)
        print(RIBLT.compare_tables(bloom1, bloom2, key)[2])
        print(asizeof.asizeof(bloom1))
        print(asizeof.asizeof(bloom2))


if __name__ == "__main__":
    BloomTest.test(test_set_size=100000)
