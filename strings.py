#!/usr/bin/env python3

import sys

size = 4
cur = []

def main(args):
	"""Checks for proper argument structure, then calls the translate function"""
	global size
	if not args and len(args) != 3:
		usage()
		sys.exit(2)
	try:
		size = int(args[1])
		with open(args[2], "rb") as fd:
			translate(fd)
	except IOError as e:
		print("IO Error: " + sys.exc_info()[0])
		sys.exit(1) #indicate an error occured
	except Exception as e:
		print("Exception raised: " + sys.exc_info()[0])
		usage()
		sys.exit(1) #indicate an error occurred

def translate(fd):
	"""reads the file 1 line at a time"""
	line = fd.readline()
	while line:
		process(line)
		line = fd.readline()


def process(line):
	"""Reads through the line 2 bytes at a time, printing all strings found"""
	global cur
	string = ""
	printRange = range(32, 127)
	for b1, b2 in zip(line[0::2], line[1::2]):
		if b1 in printRange and b2 in printRange:
			string = "%c" % b"".join(b1,b2)
		elif b1 == '00':
			string = "%c" % b2
		elif b2 == '00':
			string = "%c" % b1
		elif not (b1 in printRange and b2 in printRange):
			if len(cur) >= size:
				print(''.join(cur))
				cur = []
			continue
		cur.append(string)

def usage():
	"""Prints the usage of this script"""
	print("strings <size> <inputfile>")

if __name__ == "__main__":
	main(sys.argv)
