#!/usr/bin/python

import sys, getopt, collections

def main(argv):
	target = ""
	result = ""
	inFile = None
	outFile = None
	guess = False
	length = 0
	real = {}    # (char, float)
	expect = {}  # (char, float)
	trans = {}   # (char, char)
	expect['a'] = 0.0817
	expect['b'] = 0.0150
	expect['c'] = 0.0278
	expect['d'] = 0.0425
	expect['e'] = 0.1270
	expect['f'] = 0.0223
	expect['g'] = 0.0202
	expect['h'] = 0.0609
	expect['i'] = 0.0697
	expect['j'] = 0.0015
	expect['k'] = 0.0077
	expect['l'] = 0.0403
	expect['m'] = 0.0241
	expect['n'] = 0.0675
	expect['o'] = 0.0751
	expect['p'] = 0.0193
	expect['q'] = 0.0010
	expect['r'] = 0.0599
	expect['s'] = 0.0633
	expect['t'] = 0.0906
	expect['u'] = 0.0276
	expect['v'] = 0.0098
	expect['w'] = 0.0236
	expect['x'] = 0.0015
	expect['y'] = 0.0197
	expect['z'] = 0.0007

	try:
		opts, args = getopt.getopt(argv, "bi:o:s:")
	except getopt.GetoptError:
		print("GetoptError")
		usage()
	if len(opts) == 0:
		print("Len error")
		usage()
	for opt, arg in opts:
		#Initialize  option values
		if opt == "-i":
			try:
				inFile = open(arg, "r")
				target = inFile.read()
				print("Analyzing " + arg + "...")
			except Exception as e:
				print(e)
				sys.exit(1)
		elif opt == "-o":
			try:
				outFile = open(arg, "w")
			except Exception as e:
				print(e)
				print("Continuing without output file...")
		elif opt == "-b":
			guess = True
		elif opt == "-s":
			target = arg
			print("Analyzing string...")
	length = len(target)
	for char in target:
		#Count frequencies in target
		try:
			real[char] = real[char] + 1/length
		except KeyError:
			real[char] = 1/length
	real = sorted(real)
	for tup in real:
		#print out frequencies of target
		print(tup)
		print(tup[0])
		print(": " + tup[1])
		#print(tup[0] + "{0.04f}".format(float(tup[1])))
	if guess:
		#if instructed to take best guess at cipher, do it
		#sorts both real and expected alphabets by frequency
		#and then matches from top to bottom
		#will likely decode parts but not all of a cipher
		real = sorted(real, key=real.get)
		expect = sorted(expect, key=expect.get)
		for rTup, eTup in zip(real, expect):
			if rTup[0] in expect:
				trans[rTup[1]] = eTup[1]
		for char in target:
			result = result + trans[char]
		if outFile != None:
			outFile.write(result)
			print("Result printed to " + outFile.name)
		else:
			print(result)
	sys.exit(0)

def usage():
	print("freqa -i <inputfile> -o <outputfile> -s <string> -b") #add ceasar cipher option?
	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
