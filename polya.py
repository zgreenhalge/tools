#!\usr\bin\env python3
"""
Provides functionality for polynomial arithmetic functions, including adding and multiplying in GF(2^m)
Author: Zach Greenhalge
"""

import sys

def main(args):
	if len(args) < 3:
		usage()
		sys.exit(2)
	p1 = [int(i) for i in args[1]]
	p2 = [int(i) for i in args[2]]
	p1, p2 = lenshift(p1, p2) #ensure that polys re same length
	if   args[0] == "-d":
		res = div(p1, p2)
		print("({}) / ({}) = ({}) remainder ({})".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(res[0]), pretty_poly(res[1])))
	elif args[0] == "-ga":
		print("({}) + ({}) = ({}) in GF(2^m)".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(g_add(p1, p2))))
	elif args[0] == "-m":
		print("({}) * ({}) = ({})".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(mult(p1, p2))))
	elif args[0] == "-gm":
		if len(args) < 4:
			print("Please provide an irreducible polynomial")
			sys.exit(2)
		else:
			p3 = [int(i) for i in args[3]]
		print("({}) * ({}) mod ({}) ~= ({}) in GF(2^m)".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(p3), pretty_poly(g_mult(p1, p2, p3)[1])))
	elif args[0] == "-a":
		print("({}) + ({}) = ({})".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(add(p1, p2))))
	elif args[0] == "-s":
		print("({}) - ({}) = ({})".format(pretty_poly(p1), pretty_poly(p2), pretty_poly(sub(p1, p2))))
	else:
		usage()
		sys.exit(2)

def lenshift(poly1, poly2):
	shift = abs(len(poly1) - len(poly2))
	if   len(poly1) > len(poly2):
		poly2 = ([0] * shift) + poly2
	elif len(poly1) < len(poly2):
		poly1 = ([0] * shift) + poly1
	return poly1, poly2

def usage():
	print("gfield [-a][-ga][-s][-m][-d][-gm] poly1 poly2 [poly3]")

def add(a, b):
	c = []
	idx = 0
	for c1, c2 in zip(a, b):
		c.append((c1 + c2))
	return c

def sub(a, b):
	c = []
	idx = 0
	for c1, c2 in zip(a, b):
		c.append((c1 - c2))
	return c

def g_add(a, b):
	"""Add two polynomials in GF(2^m)"""
	c = []
	idx = 0
	for c1, c2 in zip(a, b):
		c.append((c1 + c2) % 2)
	return c

def g_mult(a, b, p):
	"""Multiply two polynomials given the irreducible polynomial of a GF"""
	c = [i % 2 for i in mult(a, b)]
	c, p = lenshift(c, p)
	return div(c, p)

def mult(a, b):
	"""Multiply two polynomials"""
	ret = [0] * (len(a)+len(b)-1)
	for orderA, coeffA in enumerate(a):
		for orderB, coeffB in enumerate(b):
			#print("ret[{}] = {} + {} % 2 = {}".format(orderA+orderB, coeffA*coeffB, ret[orderA+orderB], (coeffA*coeffB + ret[orderA+orderB]) % 2))
			ret[orderA+orderB] = (coeffA*coeffB + ret[orderA+orderB])
	#print(ret)
	return ret

def degree(poly):
	"""Find the degree of a polynomial"""
	for idx, coeff in enumerate(poly):
		if coeff == 1:
			return len(poly) - idx - 1
	return 0
 
def revDeg(poly):
	"""Returns the degree for reversed priority coefficients"""
	while poly and poly[-1] == 0:
		poly.pop()   # normalize
	return len(poly)-1

def div(N, D):
	"""Divide the two given polynomials"""
	N = N[::-1]
	D = D[::-1]
	dD = revDeg(D)
	dN = revDeg(N)
	if dD < 0: raise ZeroDivisionError
	if dN >= dD:
		q = [0] * dN
		while dN >= dD:
			d = [0]*(dN - dD) + D
			mult = q[dN - dD] = N[-1] / float(d[-1])
			d = [coeff*mult for coeff in d]
			N = [abs(coeffN - coeffd) for coeffN, coeffd in zip(N, d)]
			dN = revDeg(N)
		r = N
	else:
		q = [0]
		r = N
	q = q[::-1]
	r = r[::-1]
	return q, r

def pretty_poly(poly):
	"""Turn a poly array into human readble format"""
	ret = ""
	for idx, coeff in enumerate(poly):
		if coeff:
			if coeff == 1:
				c = ""
			else:
				c = str(coeff)
			if idx == len(poly) - 1: #add 1 instead of x^0 to the poly
				if ret == "":
					if c == "":
						ret += "1"
					else:
						ret += c
				else:
					if c == "":
						ret += "+1"
					else:
						ret += "+"+c
				break
			if idx == len(poly) - 2: #add x instead of x^1 to the poly
				if ret == "":
					ret += "{}x".format(c)
				else:
					ret += "+{}x".format(c)
				continue
			if ret == "": # first poly term
				ret += "{}x^{}".format(c, len(poly)-idx-1)
			else: #middle poly terms
				ret += "+{}x^{}".format(c, len(poly)-idx-1)
	if ret == "":
		ret = "0"
	return ret

if __name__ == '__main__':
	main(sys.argv[1:])