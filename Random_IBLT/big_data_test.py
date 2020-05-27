# Created By Nick Huppert on 13/5/20.
from random_iblt import RIBLT
import random
from random import randint


# Generate huge table of incrementing numeric IDs
big_table = []
for i in range(1000000):
    random_int = randint(1,10)
    if i != 0:
        random_int += big_table[i-1]
    big_table.append(random_int)

random.seed()
for i in range(20):
    index = randint(int(len(big_table) * 0.6), int(len(big_table) * 0.9))
    seed_key = randint(0, 1000)
    table_size = 500000
    full_bloom, seeds, hash_multiplier = RIBLT.generate_table(big_table, seed_key, table_size)
    part_bloom, x, y = RIBLT.generate_table(big_table[:index], seed_key, table_size)
    diff = RIBLT.compare_tables(full_bloom, part_bloom, seed_key, seeds, hash_multiplier)
    print(diff[2])
