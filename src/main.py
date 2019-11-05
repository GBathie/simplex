#!/usr/bin/env python3
"""
Entry point of the program
"""
import numpy as np
import random
from fractions import Fraction
from simplex import *
from parsing import *
from rules import max_coeff, bland, random_pivot, custom_pivot


if __name__ == '__main__':
	args = parse_args()
	if args:
		verbose, ifile_name, ofile_name, rule_name, solve_dual = args
		if ofile_name:
			ofile = open(ofile_name, "w+")
			stdo = sys.stdout
			sys.stdout = ofile

		lp = parse_lp(ifile_name)
		if rule_name == "Maximum coefficient":
			rule = max_coeff
		elif rule_name == "Bland's":
			rule = bland
		elif rule_name == "Random":
			random.seed()
			rule = random_pivot
		elif rule_name == "Custom":
			rule = custom_pivot
		a = simplex(lp, rule, verbose, rule_name)
		if solve_dual:
			print("--------------------")
			b = simplex(dual(lp), rule, verbose, rule_name)
		if ofile_name:
			sys.stdout = stdo
			ofile.close()