# Created By Nick Huppert on 20/7/20.
import math


class Distribution:

    @staticmethod
    def create_poisson_distribution(minimum, average):
        distributions = []
        distribution = 0
        if minimum >= max or minimum >= average:
            return distributions
        for k in range(0, int((average - minimum) * 4)):
            distribution += (math.pow((average - minimum), k) * math.exp(-(average - minimum))) / (math.factorial(k))
            distributions.append((distribution, minimum + k))

        return distributions

    @staticmethod
    def create_aloha_style_distribution(x, a, n):
        num = []
        for i in range(2, n+1):
            top = math.pow(x, i)/(i*(i-1))
            top = top - (a*math.pow(x, 2)/2)

            bot = 1/(i*(i-1))
            bot = bot - (a/2)
            num.append((i, top, bot))

        return num

    @staticmethod
    def create_robust_soliton_distribution():
        pass


if __name__ == "__main__":
    # dist = Distribution.create_poisson_distribution(2, 6)
    dist = Distribution.create_aloha_style_distribution(4, .1, 7)
    sum1 = 0
    sum2 = 0
    for item in dist:
        print(item)
        sum1 += item[1]
        sum2 += item[2]
    print(1/sum1/sum2)