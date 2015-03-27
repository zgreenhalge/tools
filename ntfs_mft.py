#! /usr/bin/env python3
"""
Author: Zach Greenhalge
Parses the MFT entries in an NTFS system
"""

import sys
from struct import unpack

bytes_per_sector    = -1
sectors_per_cluster = -1
total_sectors       = -1
MFT_start_cluster   = -1
size_MFT_entry      = -1
size_index_record   = -1

class MFTEntry:
	"""Parses an MFT entry header and creates MFTAttribute instances for all attributes in the entry"""

	def __init__(self, start, fd):
		self.start_cluster = start
		self.offset = bytes_per_sector * sectors_per_cluster * self.start_cluster
		fd.seek(self.offset, 0)
		self.signature   	= bytes.decode(fd.read(4)) #signature as string (0-3)
		self.fixup_offset	= unpack("<H", fd.read(2))[0] #relative to start of entry (4-5)
		self.fixup_entry 	= unpack("<H", fd.read(2))[0] # (6-7)
		self.LSN		 	= unpack("<Q", fd.read(8))[0] # (8-15)
		self.seq_value   	= unpack("<H", fd.read(2))[0] # (16-17)
		self.link_count		= unpack("<H", fd.read(2))[0] # (18-19)
		self.attr_offset	= unpack("<H", fd.read(2))[0] # (20-21)
		self.flags			= unpack("<H", fd.read(2))[0] #0x01 = in use, 0x02 = directory (22-23)
		self.size_used		= unpack("<L", fd.read(4))[0] # (24-27)
		self.allocated_size = unpack("<L", fd.read(4))[0] # (28-31)
		self.base_entry_ref = unpack("<Q", fd.read(8))[0] # (32-39)
		self.next_att_id    = unpack("<H", fd.read(2))[0] # (40-41)



class MFTAttribute:
	"""Parses an attribute in an MFTEntry"""

def main():
	global bytes_per_sector, sectors_per_cluster, total_sectors, MFT_start_cluster, size_of_MFT_entry, size_index_record
	if len(sys.argv) != 2:
		usage()
		sys.exit(2)
	with open(sys.argv[1], "rb") as fd:
		fd.read(3) #(3 bytes) - assembly to jump to boot code
		fd.read(8) #(8 bytes) - OEM name of drive
		bytes_per_sector    = unpack("<H", fd.read(2))[0]
		sectors_per_cluster = int(unpack("<B", fd.read(1))[0])
		fd.read(2) #(2 bytes) - reserved sectors [must be 0, according to Microsoft]
		fd.read(5) #(5 bytes) - unused
		fd.read(1) #(1 byte ) - media descriptor for dirve
		fd.read(2) #(2 bytes) - unused [must be 0: Microsoft]
		fd.read(8) #(8 bytes) - unused
		fd.read(4) #(4 bytes) - unused [must be 0: Microsoft]
		fd.read(4) #(4 bytes) - unused
		total_secotrs       = unpack("<Q", fd.read(8))[0]
		MFT_start_cluster   = unpack("<Q", fd.read(8))[0]
		fd.read(8) #(8 bytes) - start cluster of MFT mirror $DATA attribute
		size_MFT_entry      = int(unpack("<B", fd.read(1))[0])
		fd.read(3) #(3 bytes) - unused
		size_index_record   = int(unpack("<B", fd.read(1))[0])
		fd.read(3) #(3 bytes) - unused
		fd.read(8) #(8 bytes) - serial number of drive
		mft = MFTEntry(MFT_start_cluster, fd)

def usage():
	print("ntfs_mft ")

if __name__ == '__main__':
	main()