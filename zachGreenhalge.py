"""
Author: Zach Greenhalge
"""

import sys
from struct import unpack

def getSigned(bites):
	#assumes little endian
	if len(bites) > 8:
		raise Exception("Expected 8 bytes, got " + len(bites))
	elif len(bites) < 8:
		if bites[-1] >> 7 == 1:
			pad = b'\xFF'
		else:
			pad = b'\x00'
		padLength = 8-len(bites)
	return unpack("<q", bites + (pad * padLength))[0]

def main():
	print(getSigned(b'\xFF\xFF'))

if __name__ == '__main__':
	main()