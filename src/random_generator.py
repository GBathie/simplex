"""
Contains the functions for the random generation of LPs
"""

import random
import sys
from fractions import Fraction

"""
Generate a random rational :
Pick at random a denominator between 1 and d,
then pick a rational uniformly in the range b0, b1 with that denominator
"""


def random_rational(b0, b1, d):
    denom = random.randint(1, d)
    num = random.randint(b0 * denom, b1 * denom)
    return Fraction(num, denom)


"""
Generate n rationals at a time
"""


def random_n_rational(b0, b1, d, n):
    return [random_rational(b0, b1, d) for i in range(n)]


"""
Generate a LP with n variables and m constraints, write it in filename
"""


def generate_to_file(n, m, filename, b0=0, b1=10, d=1):
    f = open(filename, "w+")
    f.write(n + "\n")
    f.write(m + "\n")
    n, m = int(n), int(m)
    b0, b1 = int(b0), int(b1)
    d = max(int(d), 1)

    f.write(" ".join(list(map(str, random_n_rational(b0, b1, d, n)))) + "\n")
    f.write(" ".join(list(map(str, random_n_rational(b0, b1, d, m)))) + "\n")
    for i in range(m):
        f.write(
            " ".join(list(map(str, random_n_rational(b0, b1, d, n))))
            + " "
            + random.choice(["<", ">", "="])
            + "\n"
        )
    f.close()


if __name__ == "__main__":
    generate_to_file(*sys.argv[1:])
