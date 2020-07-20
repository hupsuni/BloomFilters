# Created By Nick Huppert on 20/7/20.
import math


class Distribution:

    @staticmethod
    def create_possion_distribution(minimum, average):
        distributions = []
        distribution = 0
        if minimum >= max or minimum >= average:
            return distributions
        for k in range(0, int((average - minimum) * 4)):
            distribution += (math.pow((average - minimum), k) * math.exp(-(average - minimum))) / (math.factorial(k))
            distributions.append((distribution, minimum + k))

        return distributions


if __name__ == "__main__":
    dist = Distribution.create_possion_distribution(2, 6)
    for item in dist:
        print(item)
