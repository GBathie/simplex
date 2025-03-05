"""
Functions for pretty printing LPs
"""


def print_initial(lp):
    obj, A, b = lp
    m, n = A.shape

    line = "Maximize "
    for i in range(n):
        line += (" +" if obj[i] >= 0 and i > 0 else " ") + str(obj[i]) + "x_" + str(i)
    print(line)

    for i in range(m):
        line = "Such that" if i == 0 else "         "
        for j in range(n):
            line += (" +" if A[i][j] >= 0 and j > 0 else " ") + str(A[i][j]) + "x_" + str(j)
        print(line + " <= " + str(b[i]))
    line = "          "
    line += ", ".join(["x_" + str(i) for i in range(n)])
    print(line + (" are " if n > 1 else " is ") + "non-negative")


def print_tableau(objv, obj, A, b, basis, outside):
    for i in range(len(basis)):
        line = "x_" + str(basis[i]) + " = " + str(b[i])
        for j in outside:
            line += (" +" if A[i][j] <= 0 else " ") + str(-A[i][j]) + "x_" + str(j)
        print(line)
    print("----------------------------------------")

    obj_f = "z = " + str(objv)
    for i in outside:
        obj_f += (" +" if obj[i] >= 0 else " ") + str(obj[i]) + "x_" + str(i)
    print(obj_f)
