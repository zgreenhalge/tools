#!/usr/bin/env python3

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
	line = fd.readline()
	while line:
		process(line)
		line = fd.readline()


def process(line):
	"""Reads through the line 1 byte at a time, printing all strings found"""
	global cur
	string = ""
	for byte in line:
		#is ' ' a valid char or is it a separator?
		if byte in range(32, 127): 
			string = byte.to_bytes(1, sys.byteorder).decode(encoding="ascii")
			cur.append(string) 
		else:
			#if byte is a non-printable char, end the string
			s = ''.join(cur)
			if len(cur) >= size:
				print(s)
			cur = []

def usage():
	"""Prints the usage of this script"""
	print("strings <size> <inputfile>")

if __name__ == "__main__":
	main(sys.argv)
