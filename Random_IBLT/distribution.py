# Created By Nick Huppert on 20/7/20.
import math


class Distribution:

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
    def create_aloha_style_distribution(x, a, n):
        num = []
        for N in range(1, n+1):
            bot = 0
            top = 0
            for i in range(2, N+1):
                top += math.pow(x, i)/(i*(i-1)) - (a*math.pow(x, 2)/2)

                bot += 1/(i*(i-1)) - (a/2)

            y = math.pow(x, 2) / (2 * (2 - 1)) - (a * math.pow(x, 2) / 2)
            z = 1 / (2 * (2 - 1)) - (a / 2)

            top2 = 0
            bot2 = 0
            for i in range(1, n+1):
                top2 += (math.pow(x, i)/i) - (a*x)
                bot2 += 1/i
            px = math.exp(-((bot2-a)*(1-x)))
            bot2 -= a
            num.append((x, top/bot, y/z, top2/bot2, px))

        return num

    @staticmethod
    def create_robust_soliton_distribution():
        pass


if __name__ == "__main__":
    # dist = Distribution.create_poisson_distribution(2, 7)
    dist = Distribution.create_aloha_style_distribution(2, .01, 5)
    sum1 = 0
    sum2 = 0
    for item in dist:
        print(item)
