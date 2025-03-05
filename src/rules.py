"""
This file contains the implementation of the different pivoting rules :
Maximum coefficient Rule, Bland's Rule, Random Rule, Custom Rule
A rule is a function that takes as arguments (obj, A, b, basis, outside)
and returns i : variable that enters the basis,
                        j : saturated equation
                        cont : False if the simplex is over
                        unbounded : True iff the optimal value is infinite
"""

import random
import numpy as np

"""
******** Generic auxiliary functions ********
"""


# Returns the list of indexes of all equations saturated by variable i
def saturated_eq(i, A, b):
    m = len(b)

    nonzero = list(filter(lambda j: A[j][i] != 0, range(m)))
    constrained = list(filter(lambda j: A[j][i] > 0, nonzero))
    if not constrained:
        return []  # Unbounded case
    coeffs = [b[j] / A[j][i] for j in constrained]
    minj = constrained[np.argmin(coeffs)]
    saturated = list(filter(lambda x: b[x] / A[x][i] == b[minj] / A[minj][i], constrained))

    return saturated


"""
******** Max coefficient rule ********
Ties are solved arbitrarily
"""


def max_coeff(obj, A, b, basis, outside):
    i = np.argmax(obj)
    if obj[i] <= 0:
        return 0, 0, False, False
    s = saturated_eq(i, A, b)
    if not s:
        return 0, 0, False, True

    j = s[0]
    return i, j, True, False


"""
******** Bland's rule ********
"""


def bland(obj, A, b, basis, outside):
    if np.max(obj) <= 0:
        return 0, 0, False, False

    i = min(list(filter(lambda x: obj[x] > 0, outside)))
    s = saturated_eq(i, A, b)
    if not s:
        return 0, 0, False, True

    j = basis.index(min([basis[l] for l in s]))
    return i, j, True, False


"""
******** Random pivot ******** 
"""


def is_unbounded(i, A, b):
    m = len(b)
    for j in range(m):
        if A[j][i] > 0:
            return False

    return True


def random_pivot(obj, A, b, basis, outside):
    if np.max(obj) <= 0:
        return 0, 0, False, False

    positive_coeffs = list(filter(lambda x: obj[x] > 0, outside))
    if not positive_coeffs:
        return 0, 0, False, False

    for i in positive_coeffs:
        if is_unbounded(i, A, b):
            return i, 0, False, True

    i = random.choice(positive_coeffs)
    s = saturated_eq(i, A, b)
    j = random.choice(s)

    return i, j, True, False


"""
******** Custom rule ********
-> Accelerated Bland's rule
"""


def max_increase(i, A, b):
    m = len(b)
    nonzero = list(filter(lambda j: A[j][i] != 0, range(m)))
    constrained = list(filter(lambda j: A[j][i] > 0, nonzero))
    if not constrained:
        return float("inf")
    coeffs = [b[j] / A[j][i] for j in constrained]
    return min(coeffs)


def custom_pivot(obj, A, b, basis, outside):
    if np.max(obj) <= 0:
        return 0, 0, False, False

    inc = [max_increase(i, A, b) if obj[i] > 0 else -1 for i in outside]
    i = outside[np.argmax(inc)]
    s = saturated_eq(i, A, b)
    if not s:
        return 0, 0, False, True

    j = basis.index(min([basis[l] for l in s]))
    return i, j, True, False
