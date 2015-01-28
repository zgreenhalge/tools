#!/usr/bin/python

import sys

linen = 0
linef = "{0:08X}  {1:s}  |{2:s}|" #line no, hex bytes, ASCII chars
hexLine = "{} {} {} {} {} {} {} {}  {} {} {} {} {} {} {} {}" #16 hex bytes, string format to accept blanks at EOF

def main(args):
	#Checks for proper argument structure, then calls the translate function
	if len(args) != 2:
		usage()
		sys.exit(2)
	try:
		with open(args[1], "rb") as fd:
			translate(fd)
	except IOError as e:
		print("Exception raised: " + e)

def translate(fd):
	#reads the file 16 bytes at a time, and prints out the values
	global linen
	line = fd.read(16)
	while line:
		printLine(line)
		linen += 1
		line = fd.read(16)


def printLine(line):
	#prints the given line of bytes in proper format
	ascArr = [None] * len(line)
	hexStrs  = [None] * 16
	for idx, byte in enumerate(line):
		#go through line, decode byte to ASCII and check if valid
		#then convert bytes to HEX
		try:
			string = byte.to_bytes(1, sys.byteorder).decode(encoding="ascii")
			if not string.isalnum():
				string = "."
		except UnicodeDecodeError:
			#catch exception thrown by non-ASCII
			string = "."
		hexStrs[idx] = "%02X" % byte
		ascArr[idx] = string
	if len(line) < 16: 
	#fill hexStrs for EOF case
		for i in range(len(line)-1, 16):
			hexStrs[i] = "  "
	#Setup is complete, print with pre-made format strings
	lineVal = linef.format(linen, hexLine.format(*hexStrs), ''.join(ascArr))
	print(lineVal)

def find(char, string):
	#Finds all instances of char in the given string
	ret = []
	for i, c in enumerate(string):
		if c == char:
			ret.append(i)
	return ret

def usage():
	#mandatory input file
	print("hexdump <inputfile>")

if __name__ == "__main__":
	main(sys.argv)
