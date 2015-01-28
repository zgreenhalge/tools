#!/usr/bin/python

import sys

size = 4
cur = []

def main(args):
	"""Checks for proper argument structure, then calls the translate function"""
	global size
	if len(args) != 3:
		usage()
		sys.exit(2)
	try:
		size = int(args[1])
		with open(args[2], "rb") as fd:
			translate(fd)
	except IOError as e:
		print("Exception raised: " + str(e))
		sys.exit(1) #indicate an error occured
	except Exception as e:
		print("Exception raised: " + str(e))
		usage()
		sys.exit(1) #indicate an error occurred

def translate(fd):
	"""reads the file 1 line at a time"""
	line = fd.readLine()
	while line:
		process(line)
		line = fd.readLine()


def process(line):
	"""Reads through the line 1 byte at a time, printing all strings found"""
	global cur
	for byte in line:
		if byte >= 32 and byte <= 126:
			string = byte.to_bytes(1, sys.byteorder).decode(encoding="ascii")
		if string != " ":
			cur.append(string)
		else:
			s = ''.join(cur)
			if len(s) >= size:
				print(s)
			cur = []

def usage():
	"""Prints the usage of this script"""
	print("strings <size> <inputfile>")

if __name__ == "__main__":
	main(sys.argv)
