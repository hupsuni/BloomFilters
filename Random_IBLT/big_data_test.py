# Created By Nick Huppert on 13/5/20.
from iblt import IBloomLT
from random import randint
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
hash_func_count = 7
with open(os.path.join(current_dir, "words.txt"), "r") as word_file:
    words = word_file.readlines()
iblt = IBloomLT(m=int(len(words) * .3), k=hash_func_count)
hashed_words = []
i = 0
for word in words:
    hashed_words.append(i)
    i += 1

index = randint(int(len(words) * 0.8), int(len(words)))

all_but_one = hashed_words[:len(words) - 1]
incomplete_words = hashed_words[:index]

full_table = iblt.generate_table(hashed_words)
abo_table = iblt.generate_table(all_but_one)
incomplete_table = iblt.generate_table(incomplete_words)
print(len(words))
print(iblt.compare_tables(full_table, abo_table))
difference = (iblt.compare_tables(full_table, incomplete_table))
print(difference)
print(str(index) + " : " + str(len(words) - len(difference[0])))
print(difference[2])
