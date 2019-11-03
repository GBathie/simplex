"""
Parse LP files or command line arguments
"""

import sys
import numpy as np
from fractions import Fraction

def print_usage():
	print("Usage : python3 main.py input_file [-v] [-m/b/r/c] [-d] [-o filename]")


def parse_args():
	verbose = "-v" in sys.argv
	dual 	= "-d" in sys.argv

	rule_name = None
	if "-m" in sys.argv:
		rule_name = "Maximum coefficient" 
	if "-b" in sys.argv:
		rule_name = "Bland's" 
	if "-c" in sys.argv:
		rule_name = "Custom" 
	if ("-r" in sys.argv) or (not rule_name):
		rule_name = "Random"
	
	if (len(sys.argv) > 1):
		ifile_name = sys.argv[1]
	else:
		print("Not enough arguments.")
		print_usage()
		return None

	ofile_name = None
	if "-o" in sys.argv:
		i = sys.argv.index("-o")
		if (len(sys.argv) > i+1):
			ofile_name = sys.argv[i+1]
		else:
			print("Missing output file name.")
			print_usage()
			return None

	return (verbose, ifile_name, ofile_name, rule_name, dual)

def parse_lp(filename):
	f = open(filename, "r")
	lines = f.readlines();
	f.close()

	# params
	n, m = int(lines[0]), int(lines[1])
	obj = np.array(list(map(Fraction, lines[2].split())))
	# Build the constraint matrix for only <= constraints
	# and the corresponding b vector
	coeffsb = list(map(Fraction, lines[3].split()))
	tmpA = []
	tmpB = []
	for i in range(m):
		coeffs = lines[4+i].split()
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
