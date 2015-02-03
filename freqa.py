#!/usr/bin/python
"""
Author: Zach Greenhalge
A script to perform character frequency analysis on a body of text
"""

import sys, getopt, collections
	
digrams = False
trigrams = False
inverse = False
whitespace = False
sort = lambda item: item[0]

def main(argv):
	global digrams, trigrams, sort, inverse, whitespace
	target = ""
	inFile = None
	
	#English language values
	# expect['a'] = 0.0817
	# expect['b'] = 0.0150
	# expect['c'] = 0.0278
	# expect['d'] = 0.0425
	# expect['e'] = 0.1270
	# expect['f'] = 0.0223
	# expect['g'] = 0.0202
	# expect['h'] = 0.0609
	# expect['i'] = 0.0697
	# expect['j'] = 0.0015
	# expect['k'] = 0.0077
	# expect['l'] = 0.0403
	# expect['m'] = 0.0241
	# expect['n'] = 0.0675
	# expect['o'] = 0.0751
	# expect['p'] = 0.0193
	# expect['q'] = 0.0010
	# expect['r'] = 0.0599
	# expect['s'] = 0.0633
	# expect['t'] = 0.0906
	# expect['u'] = 0.0276
	# expect['v'] = 0.0098
	# expect['w'] = 0.0236
	# expect['x'] = 0.0015
	# expect['y'] = 0.0197
	# expect['z'] = 0.0007

	try:
		opts, args = getopt.getopt(argv, "i:s:dtfw")
	except getopt.GetoptError:
		print("GetoptError")
		usage()
	if len(opts) == 0:
		print("Len error")
		usage()
	for tup in opts:
		#Initialize  option values
		if tup[0] == "-i":
			try:
				inFile = open(tup[1], "r")
				target = inFile.read()
				print("Analyzing " + tup[1] + "...")
			except Exception as e:
				print(e)
				sys.exit(1)
		elif tup[0] == "-s":
			target = tup[1]
			print("Analyzing string...")
		elif tup[0] == "-d":
			digrams = True
		elif tup[0] == "-t":
			trigrams = True
		elif tup[0] == "-f":
			sort = lambda item: item[1]
			inverse = True
		elif tup[0] == "-w":
			whitespace = True
	process(target)

def process(target):
	freq = {}
	length = len(target)
	for c in target:
		#Count frequencies in target
		char = c.lower()
		if not whitespace and char.isspace():
			continue
		if char in freq:
			freq[char] = freq[char] + 1/length
		else:
			freq[char] = 1/length
	freq = sorted(freq.items(), key=sort, reverse=inverse)
	print("{:04d} distinct characters found out of {:} total characters".format(len(freq), length))
	print("-"*40)
	for tup in freq:
		#print out frequencies of target
		print(tup[0] + ": {:8.04f}".format(tup[1]))

def usage():
	print("freqa [-i <inputfile>] [-s <string>] [-d] [-t] [-f] [-w]")
	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
