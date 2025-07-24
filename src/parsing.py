"""
Parse LP files or command line arguments
"""

import numpy as np
from fractions import Fraction
from argparse import ArgumentParser


def print_usage():
    print("Usage : python3 main.py input_file [-v] [-m/b/r/c] [-d] [-o filename]")


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("input_file", type=str, help="Path of the input file to read")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print debug information while solving"
    )
    parser.add_argument(
        "-d", "--dual", action="store_true", help="Solve the dual problem instead of the primal"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-m", "--max_coeff", action="store_true", help="Use the Maximum Coefficient pivot rule"
    )
    group.add_argument("-b", "--bland", action="store_true", help="Use Bland's pivot rule")
    group.add_argument("-c", "--custom", action="store_true", help="Use a custom pivot rule")
    group.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Use the random pivot rule (default)",
        default=True,
    )

    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="Path of the file to write the solution to",
        default=None,
    )

    args = parser.parse_args()
    dual = args.dual
    verbose = args.verbose
    ifile_name = args.input_file

    rule_name = None
    if args.max_coeff:
        rule_name = "Maximum coefficient"
    elif args.bland:
        rule_name = "Bland's"
    elif args.custom:
        rule_name = "Custom"
    elif args.random:
        rule_name = "Random"

    ofile_name = args.output_file

    return (verbose, ifile_name, ofile_name, rule_name, dual)


def parse_lp(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    # params
    _, m = int(lines[0]), int(lines[1])
    obj = np.array(list(map(Fraction, lines[2].split())))
    # Build the constraint matrix for only <= constraints
    # and the corresponding b vector
    coeffsb = list(map(Fraction, lines[3].split()))
    tmpA = []
    tmpB = []
    for i in range(m):
        coeffs = lines[4 + i].split()
        ineq = coeffs[-1][0]
        constr = []
        constr = list(map(Fraction, coeffs[:-1]))
        if ineq == "<" or ineq == "=":
            tmpA.append(constr)
            tmpB.append(coeffsb[i])
        if ineq == ">" or ineq == "=":
            tmpA.append([-i for i in constr])
            tmpB.append(-coeffsb[i])

    A = np.array(tmpA)
    b = np.array(tmpB)

    return obj, A, b
