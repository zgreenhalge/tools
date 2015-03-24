#!/usr/bin/env python3
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
english = {}
english['a'] = 0.0817
english['b'] = 0.0150
english['c'] = 0.0278
english['d'] = 0.0425
english['e'] = 0.1270
english['f'] = 0.0223
english['g'] = 0.0202
english['h'] = 0.0609
english['i'] = 0.0697
english['j'] = 0.0015
english['k'] = 0.0077
english['l'] = 0.0403
english['m'] = 0.0241
english['n'] = 0.0675
english['o'] = 0.0751
english['p'] = 0.0193
english['q'] = 0.0010
english['r'] = 0.0599
english['s'] = 0.0633
english['t'] = 0.0906
english['u'] = 0.0276
english['v'] = 0.0098
english['w'] = 0.0236
english['x'] = 0.0015
english['y'] = 0.0197
english['z'] = 0.0007

def main(argv):
	global digrams, trigrams, sort, inverse, whitespace
	target = ""
	inFile = None
	

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
			print(len(target))
			target = target.split()
			print(len(target))
	process(target)

def process(target):
	freq = {}
	length = len(target)
	for c in target:
		#Count frequencies in target
		char = c.lower()
		if char in freq:
			freq[char] = freq[char] + 1/length
		else:
			freq[char] = 1/length
	freq = sorted(freq.items(), key=sort, reverse=inverse)
	print("{:04d} distinct characters found out of {:} total characters".format(len(freq), length))
	print("-"*40)
	for tup in freq:
		#print out frequencies of target
		print("'{}': {:8.04f}".format(tup[0], tup[1]))

def usage():
	print("freqa [-i <inputfile>] [-s <string>] [-d] [-t] [-f] [-w]")
	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
