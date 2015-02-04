#!/usr/bin/env python3

import sys, traceback

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
		print("IO Error: " + sys.exc_info()[1])
		sys.exit(1) #indicate an error occured
	except Exception as e:
		print("Exception raised: " + str(sys.exc_info()[1]))
		traceback.print_tb(sys.exc_info()[2])
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
	last = "00"
	printRange = range(32, 127)
	for byte in line:
		if byte in printRange: 
			string = byte.to_bytes(1, sys.byteorder).decode(encoding="ascii")
			cur.append(string) 
		elif last not in printRange and len(cur) >= size:
			#if byte is a non-printable char, end the string
			print(''.join(cur))
			cur = []
		last = byte
	if len(cur) >= size: #final print for EOF
		print(''.join(cur))

def usage():
	"""Prints the usage of this script"""
	print("strings <size> <inputfile>")

if __name__ == "__main__":
	main(sys.argv)
