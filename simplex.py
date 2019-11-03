import numpy as np
from fractions import Fraction
from display import *

def dual(lp):
	obj, A, b = lp
	return (-b, -A.T, -obj)

def canonical_form(lp):
	obj, A, b = lp
	m, n = A.shape

	# Add slack variables
	objp = np.zeros(n+m, dtype=np.int) + Fraction()
	objp[0:n] = obj
	
	Ap = np.zeros((m, n+m), dtype=np.int) + Fraction()
	Ap[0:m, 0:n] = A
	for i in range(m):
		Ap[i,n+i] = 1
	
	bp = np.array(b)	
	return (objp, Ap, bp)

def prepare_phase_i(lp):
	obj, A, b = lp
	m, n = A.shape
	"""
	Ap = np.zeros((m, n+m), dtype=np.int) + Fraction()
	Ap[0:m, 0:n] = A
	bp = np.array(b)
	for i in range(m):
		if bp[i] < 0:
			Ap[i, n + i] = -1
			Ap[i] *= -1
			bp[i] *= -1
		else:
			Ap[i, n + i] = 1

	objp = np.zeros(n+m, dtype=np.int) + Fraction()
	objv = Fraction(0)
	for i in range(m):
		objp[0:n] += Ap[i][0:n]
		objv -= bp[i]

	return (objv, (objp, Ap, bp), list(range(n, m+n)))

	"""
	additonal_variables = []
	basis = [0]*m
	for i in range(m):
		if A[i][n-m+i]*b[i] < 0:
			basis[i] = n + len(additonal_variables)
			additonal_variables.append((i, n+len(additonal_variables)))
		else:
			basis[i] = n-m+i 

	# If phase I is not needed
	if len(additonal_variables) == 0:
		return None
	# Add slack variables
	Ap = np.zeros((m, n+len(additonal_variables)), dtype=np.int) + Fraction()
	Ap[0:m, 0:n] = A
	bp = np.array(b)
	# Set objective function to -Sum u_i
	objp = np.zeros(n+len(additonal_variables), dtype=np.int) + Fraction()
	objv = Fraction(0,1)
	for (i,j) in additonal_variables:
		c = 1 if bp[i] >= 0 else -1
		Ap[i,j] = c
		Ap[i]= c*Ap[i]
		bp[i] = c*bp[i]
	
		objp[0:n] += Ap[i][0:n]
		objv = objv - bp[i]

	return (objv, (objp, Ap, bp), basis)
	
def after_phase_i(lp, basis, t):
	obj, A, b = lp
	m, n = A.shape

	objv_r = Fraction(0)
	obj_r, A_r, b_r = np.zeros(n, dtype=np.int) + Fraction(), np.array(A), np.array(b)
	obj_r[:len(obj)] = obj

	for i in range(t, n):
		A_r[:, i] = np.zeros(m, dtype=np.int) + Fraction()
	
	# Force the phase I variables out of the basis
	for j in range(m):
		if basis[j] >= t:
			li = list(filter(lambda x: A_r[j][x] != 0, list(range(t))))
			i = li[0]

			# normalize equation j
			v = A_r[j][i]
			b_r[j] /= v
			A_r[j] /= v

			# update objective function :
			v = obj_r[i]
			objv_r += b_r[j]*v
			obj_r += -A_r[j]*v
			assert(obj_r[i] == 0)
			# update constraints
			for l in range(m):
				if l != j:
					v = A_r[l][i]
					A_r[l] += -A_r[j]*v
					b_r[l] += -b_r[j]*v

	for i in range(m):
		objv_r += obj_r[basis[i]]*b_r[i]
		obj_r += -obj_r[basis[i]]*A_r[i]

	return objv_r, basis, (obj_r, A_r, b_r)

"""
Solve one phase on the simplex, starting from given basis, default basis if None 
"""
def simplex_solver(lp, objv, basis, rule, verbose, phaseI, forbidden=[]):
	obj, A, b = lp
	m, n = A.shape

	outside = list(filter(lambda x: x > -1, [i if not i in basis else -1 for i in range(n)]))

	if verbose:
		print("The initial dictionary for phase " + ("I" if phaseI else "II") + " is:\n")
		print_tableau(objv, obj, A, b, basis, outside)
	

	pivot_count = 0
	cont = True
	while cont:
		i, j, cont, unbounded = rule(obj, A, b, basis, outside)
		if unbounded: 
			return (0, None, (0,0,0), "Unbounded", pivot_count+1)
		if not cont: #Simplex is over
			break
		pivot_count += 1

		# normalize equation j
		v = A[j][i]
		b[j] /= v
		A[j] /= v

		# update objective function :
		v = obj[i]
		objv += b[j]*v
		obj += -A[j]*v
		assert(obj[i] == 0)
		# update constraints
		for l in range(m):
			if l != j:
				v = A[l][i]
				A[l] += -A[j]*v
				b[l] += -b[j]*v

		# update basis
		tmp = basis[j] # variable associated with jth constraint
		basis[j] = i
		outside.remove(i)
		outside.append(tmp)
		outside.sort()

		if verbose:
			print()
			print("The entering variable is x_" +str(i))
			print("The leaving  variable is x_" +str(tmp))
			print()
			print_tableau(objv, obj, A, b, basis, outside)


	return (objv, basis, (obj, A, b), "Done", pivot_count)


def sanity_check(opt, n, lp):
	#######################
	xsol = np.array(list(map(lambda x: x[1], opt[:n])))
	check = lp[1].dot(xsol)	
	print("Sanity check: ",  check <= lp[2])
	print(" ".join(list(map(str, check))))
	print("Sanity check2: ",  xsol >= np.zeros_like(xsol))
	#######################

def simplex(lp, rule, verbose, rule_name):
	print("The input linear program is :\n")
	print_initial(lp)
	print()
	# Original
	obj, A, b = lp
	m,n = A.shape
	# Canonical
	objc, Ac, bc = canonical_form(lp)
	mc, nc = Ac.shape
	
	# Phase I
	res = prepare_phase_i((objc, Ac, bc))
	if res : 
		objv1, (obj1, A1, b1), basis1 = res
		objv2, basis2, (_, A2, b2), _, c1 = simplex_solver((obj1, A1, b1), objv1, basis1, rule, verbose, True)
		if verbose:
			print("\nPhase I is over\n")
		if objv2 < 0:
			print("The linear program is UNFEASIBLE")
			print("Number of pivots :", c1)
			print("Pivot function used :", rule_name)
			return "UNF"
		objv3, basis3, (obj3, A3, b3) = after_phase_i((objc, A2, b2), basis2, nc)

	else:
		if verbose:
			print("Phase I is not necessary\n")
		obj3, objv3 = objc, Fraction(0)
		A3, b3 = Ac, bc
		basis3 = list(range(n, n+m))
		c1 = 0

	# phase II
	objv, basis_res, (_, A_res, b_res), status, c2 = simplex_solver((obj3, A3, b3), objv3, basis3, rule, verbose, False)
	if status == "Unbounded":
		print("The linear program is FEASIBLE, the objective function is UNBOUNDED")
		objv = float("inf")
	else:
		opt = [(i,0) for i in range(n)]
		for i in range(m):
			if basis_res[i] < n:
				opt[basis_res[i]] = (basis_res[i],b_res[i])
		print("The linear program is FEASIBLE")
		print("An optimal solution is " + ", ".join(list(map(lambda x: "x_" + str(x[0]) + " = " + str(x[1]),opt))))
		print("Optimal value : " + str(objv))
		if verbose: sanity_check(opt, n, lp)
	print("Number of pivots :", c1 + c2)
	print("Pivot function used :", rule_name)
	return objv