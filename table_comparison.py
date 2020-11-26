import json
from datetime import datetime
from aloha_iblt import IBLT as ALOHA
from iblt import IBloomLT as IBLT
from random_iblt import RIBLT
from random import randint, seed, shuffle
from threadsafe_dictionary import TSDict
from concurrent import futures
import threading

DEFAULT_TEST_SIZE = 1000000
DEFAULT_SYMMETRIC_DIFFERENCE = .4
DEFAULT_BLOOM_SIZE = .6
DEFAULT_REPS = 10
DEFAULT_A_VALUE = 0
DEFAULT_MAX_HASHES = 10

test_number = 0

results_dictionary = TSDict.instance()


# results_dictionary = {
#     "IBLT": {
#
#     },
#     "ALOHA": {
#
#     },
#     "RIBLT": {
#
#     }
# }


def dictionary_test_key():
    """
    Get a dictionary key based on test being performed.
    Returns:

    """
    return str(test_number)


def verify_results(test_data, result):
    success = True

    if len(result[0]) == len(test_data[3]) and len(result[1]) == len(test_data[4]):
        for item in result[0]:
            if item not in test_data[3]:
                success = False
                break
        for item in result[1]:
            if item not in test_data[4] or success is False:
                success = False
                break

    if result[2] == "Failed":
        return success, "Table reported Failure", False
    elif result[2] == "Success":
        return success, "Table reported Success", True


def test(reps=DEFAULT_REPS, bloom_size=DEFAULT_BLOOM_SIZE, sym_difference=DEFAULT_SYMMETRIC_DIFFERENCE,
         a_value=DEFAULT_A_VALUE, max_hashes=DEFAULT_MAX_HASHES, only_test_aloha=False, test_string=None):
    # Bloom Table: Create time, compare time, success count, [success messages]
    counters = {"IBLT": [0, 0, 0, []],
                "RIBLT": [0, 0, 0, []],
                "ALOHA": [0, 0, 0, []]}
    key_string = str(test_string)
    for i in range(0, reps):
        print("Iteration %s" % str(i))
        key = randint(1, 100000)
        test_data = generate_test_data(symmetric_difference=sym_difference)
        table_size = int(len(test_data[0]) * bloom_size)
        if only_test_aloha is False:
            IBLT_object = IBLT(m=table_size)

            start = datetime.now()
            IBLT_a = IBLT_object.generate_table(test_data[0])
            IBLT_b = IBLT_object.generate_table(test_data[1])
            stop = datetime.now()
            time_taken = stop - start

            start = datetime.now()
            results = IBLT_object.compare_tables(IBLT_a, IBLT_b)
            stop = datetime.now()

            counters["IBLT"][0] += time_taken.microseconds
            counters["IBLT"][1] += (stop - start).microseconds

            verify = verify_results(test_data, results)
            if verify[0] == verify[2] and verify[0] is True:
                counters["IBLT"][2] += 1

            counters["IBLT"][3].append(verify)

            start = datetime.now()
            RIBLT_b = RIBLT.generate_table(test_data[0], key, table_size=table_size, max_hashes=max_hashes)
            RIBLT_a = RIBLT.generate_table(test_data[1], key, table_size=table_size, max_hashes=max_hashes)
            stop = datetime.now()
            time_taken = stop - start

            start = datetime.now()
            results = RIBLT.compare_tables(RIBLT_a[0], RIBLT_b[0], seed_key=key, max_hashes=max_hashes)
            stop = datetime.now()

            counters["RIBLT"][0] += time_taken.microseconds
            counters["RIBLT"][1] += (stop - start).microseconds

            verify = verify_results(test_data, results)
            if verify[0] == verify[2] and verify[0] is True:
                counters["RIBLT"][2] += 1

            counters["RIBLT"][3].append(verify)

        start = datetime.now()
        ALOHA_a = ALOHA.generate_table(test_data[0], key, table_size=table_size, max_hashes=max_hashes, a_value=a_value)
        ALOHA_b = ALOHA.generate_table(test_data[1], key, table_size=table_size, max_hashes=max_hashes, a_value=a_value)
        stop = datetime.now()
        time_taken = stop - start

        start = datetime.now()
        results = ALOHA.compare_tables(ALOHA_a[0], ALOHA_b[0], seed_key=key, max_hashes=max_hashes, a_value=a_value)
        stop = datetime.now()

        counters["ALOHA"][0] += time_taken.microseconds
        counters["ALOHA"][1] += (stop - start).microseconds

        verify = verify_results(test_data, results)
        if verify[0] == verify[2] and verify[0] is True:
            counters["ALOHA"][2] += 1

        counters["ALOHA"][3].append(verify)

    # Tests are:
    # Bloom filter table size
    # Symmetric Difference Size
    # A Values
    # Max Hashes

    for table in counters.keys():
        if only_test_aloha and table != "ALOHA":
            continue
        results_dictionary.set(table, key_string, "average_creation_time", counters[table][0] / reps)
        results_dictionary.set(table, key_string, "average_comparison_time", counters[table][1] / reps)
        results_dictionary.set(table, key_string, "success_rate", counters[table][2] / reps)
        results_dictionary.set(table, key_string, "success_messages", counters[table][3].copy())
        results_dictionary.set(table, key_string, "filter_size", bloom_size)
        results_dictionary.set(table, key_string, "symmetric_difference", sym_difference)
        results_dictionary.set(table, key_string, "a_value", a_value)
        results_dictionary.set(table, key_string, "max_hashes", max_hashes)


def generate_test_data(quantity=DEFAULT_TEST_SIZE, symmetric_difference=DEFAULT_SYMMETRIC_DIFFERENCE):
    """
    Returns 5 lists, first two are lists with predefined overlap for blook table testing, the third list is all
    the duplicate items shared by these 2 lists, the final 2 lists are only the unique values from list a and b.

    Args:
        quantity:
        symmetric_difference:

    Returns:

    """
    seed()
    # Populate a list of randomly generated increasing numbers.
    full_list = []
    last_number = 0
    for i in range(0, 2 * quantity):
        rand_increment = randint(0, 100)
        last_number += rand_increment
        full_list.append(last_number)

    second_list_indices = (int(quantity * symmetric_difference), int(quantity + quantity * symmetric_difference))

    shuffle(full_list)

    list_a = full_list[0:quantity]
    list_b = full_list[second_list_indices[0]:second_list_indices[1]]
    duplicates = full_list[second_list_indices[0]:quantity]
    a_unique = full_list[0:second_list_indices[0]]
    b_unique = full_list[quantity:second_list_indices[1]]

    return list_a.copy(), list_b.copy(), duplicates.copy(), a_unique.copy(), b_unique.copy()


if __name__ == '__main__':

    table_size_minmax = (40, 56, 1)
    symmetric_difference_minmax = (45, 65, 1)
    max_hash_minmax = (3, 15, 1)
    a_value_minmax = (-10, 10, 2)

    # futures_list = []

    aloha_only = False

    # Test everything in one big loop
    for bl_size in range(table_size_minmax[0], table_size_minmax[1], table_size_minmax[2]):
        test_number += 1

        test(bloom_size=bl_size / 100, a_value=0, max_hashes=12, only_test_aloha=aloha_only)
    for sym_diff in range(symmetric_difference_minmax[0], symmetric_difference_minmax[1],
                          symmetric_difference_minmax[2]):

        test_number += 1

        test(sym_difference=sym_diff / 100, a_value=0, max_hashes=12, only_test_aloha=aloha_only)

    for max_hash in range(max_hash_minmax[0], max_hash_minmax[1], max_hash_minmax[2]):
        for a_val in range(a_value_minmax[0], a_value_minmax[1], a_value_minmax[2]):
            if a_val == a_value_minmax[0]:
                aloha_only = False
            else:
                aloha_only = True
            test_number += 1
            test(a_value=a_val, max_hashes=max_hash, only_test_aloha=aloha_only)
    with open("test_data.json", "w") as dump_data:
        dump_data.write(json.dumps(results_dictionary.get_all()))
