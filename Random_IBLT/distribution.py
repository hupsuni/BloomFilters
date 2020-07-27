# Created By Nick Huppert on 20/7/20.
import math
from random import randint, seed


class Distribution:

    MAXIMUM_ACCURACY = 10000000

    @staticmethod
    def create_poisson_distribution(minimum, average):
        distributions = []
        distribution = 0
        if minimum >= average:
            return distributions
        for k in range(0, (int(average-minimum) * 2) + 2):
            distribution += (math.pow((average - minimum), k) * math.exp(-(average - minimum))) / (math.factorial(k))
            distributions.append((distribution, minimum + k))

        return distributions

    @staticmethod
    def create_aloha_style_distribution(a, n):
        num = []

        denominator = 0
        for i in range(2, n+2):
            denominator += 1/(i*(i-1)) - (a/2)

        numerator = 0
        for i in range(2, n+2):
            numerator += 1/(i*(i-1)) - a/2
            num.append((i, numerator, denominator, numerator / denominator))

        return num

    @staticmethod
    def create_randomly_generated_sequence(size, minimum, maximum, a_value, seed_value):
        if maximum <= minimum:
            return None
        distribution_list = Distribution.create_aloha_style_distribution(a_value, (maximum-minimum)+1)
        seed(seed_value)
        hash_list = []
        for i in range(0, size):
            random_number = randint(0, Distribution.MAXIMUM_ACCURACY)
            random_number = random_number/Distribution.MAXIMUM_ACCURACY
            for j in range(0, len(distribution_list)):
                if random_number <= distribution_list[j][3]:
                    hash_list.append(distribution_list[j][0]-2+minimum)
                    break

        return hash_list

if __name__ == "__main__":

    dist = Distribution.create_aloha_style_distribution(-1, 11)
    seed()
    seed_value = randint(0, 10000)
    hash_array = Distribution.create_randomly_generated_sequence(2000, 2, 12, -1, seed_value)
    print(hash_array)
    print(len(hash_array))
    sum1 = 0
    sum2 = 0
    last = 0
    for item in dist:
        print(item)
        last = item[3]-sum1
        sum1 += last
        print(last)
    print(sum1)
