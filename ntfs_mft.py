#! /usr/bin/env python3
"""
Author: Zach Greenhalge
Parses the MFT entries in an NTFS system
"""

import sys, math, traceback
from struct import unpack

bytes_per_sector    = -1
sectors_per_cluster = -1
total_sectors       = -1
MFT_start_cluster   = -1
size_MFT_entry      = -1
size_index_record   = -1
debug = True

attr_name = {}
attr_name[16]  = "$STANDARD_INFORMATION"
attr_name[32]  = "$ATTRIBUTE_LIST"
attr_name[48]  = "$FILE_NAME"
attr_name[64]  = "$OBJECT_ID"
attr_name[80]  = "$SECURITY_DESCRIPTOR"
attr_name[96]  = "$VOLUME_NAME"
attr_name[112] = "$VOLUME_INFORMATION"
attr_name[128] = "$DATA"
attr_name[144] = "$INDEX_ROOT"
attr_name[160] = "$INDEX_ALLOCATION"
attr_name[176] = "$BITMAP"
attr_name[192] = "$REPARSE_POINT"
attr_name[256] = "$LOGGED_TOOL_STREAM"

class MFTEntry:
	"""Parses an MFT entry header and creates MFTAttribute instances for all attributes in the entry"""
	printStr = "Sequence: {}\n$LogFile Sequence Number: {}\n{}\nUsed Size: {}\nAllocated Size: {}\n"

	def __init__(self, start, fd):
		self.start_cluster  = start
		self.offset 		= bytes_per_sector * sectors_per_cluster * self.start_cluster
		fd.seek(self.offset, 0)
		self.raw			= fd.read(size_MFT_entry)
		# print(repr(self.raw))

		self.signature   	= bytes.decode(self.raw[0:4]  ) #signature as string (0-3)
		self.fixup_offset	= unpack("<H", self.raw[4:6]  )[0] #relative to start of entry (4-5)
		self.fixup_entry 	= unpack("<H", self.raw[6:8]  )[0] # (6-7)
		self.LSN		 	= unpack("<Q", self.raw[8:16] )[0] # (8-15)
		self.seq_value   	= unpack("<H", self.raw[16:18])[0] # (16-17)
		self.link_count		= unpack("<H", self.raw[18:20])[0] # (18-19)
		self.attr_offset	= unpack("<H", self.raw[20:22])[0] # (20-21)
		self.flags			= unpack("<2B", self.raw[22:24])    #0x01 = in use, 0x02 = directory (22-23)
		self.size_used		= unpack("<l", self.raw[24:28])[0] # (24-27)
		self.allocated_size = unpack("<L", self.raw[28:32])[0] # (28-31)
		self.base_entry_ref = unpack("<Q", self.raw[32:40])[0] # (32-39)
		self.next_att_id    = unpack("<H", self.raw[40:42])[0] # (40-41)
		self.flagStr = ""
		if self.flags[0] == 1 or self.flags[1] == 1:
			self.flagStr += "Allocated\n"
		if self.flags[0] == 2 or self.flags[1] == 2:
			self.flagStr += "Directory\n"
		print("MFT Entry Header Values:")
		print(self.printStr.format(self.seq_value, self.LSN, self.flagStr, self.size_used, self.allocated_size))

		fixup_array = self.raw[self.fixup_offset:self.fixup_offset+(self.fixup_entry*2)]
		fixup_signature = unpack(">H", fixup_array[0:2])[0]
		fixup_sec1	= unpack(">H", fixup_array[2:4])[0]
		fixup_sec2	= unpack(">H", fixup_array[4:])[0]
		tail_1		= unpack(">H", self.raw[510:512])[0]
		tail_2		= unpack(">H", self.raw[1022:1024])[0]
		if debug:
			print("Fixup signature: 0x{:04X}; 510/511: 0x{:04X}; 1022/1023: 0x{:04X}".format(fixup_signature, tail_1, tail_2))
			print("Writing 0x{:04X} into bytes 510/511; Writing 0x{:04X} into bytes 1022/1023".format(fixup_sec1, fixup_sec2))
			print()

		self.attributes = []
		self.attributes.append(MFTAttribute(self.attr_offset, self))
		
	def add_attribute(attribute):
		self.attributes.append(attribute)


class MFTAttribute:
	"""Parses an attribute in an MFTEntry"""
	attr = {
		16:  std_info,
		32:  attr_list,
		48:  file_name,
		64:  object_id,
		80:  security_desc,
		96:  vol_name,
		112: vol_info,
		128: data,
		144: index_root,
		160: index_alloc,
		176: bitmap,
		192: reparse_pt,
		256: logged_tool_stream,
	}

	def __init__(self, start, parent):
		self.parent 	= parent
		self.offset 	= start
		
		# Attribute header: frist 16 bytes
		self.type_ID	= unpack("<L", parent.raw[self.offset:self.offset+4]    )[0]
		self.length		= unpack("<L", parent.raw[self.offset+4:self.offset+8]  )[0]
		self.nonresident= unpack("<b", parent.raw[self.offset+8:self.offset+9]  )[0]
		self.name_len	= unpack("<b", parent.raw[self.offset+9:self.offset+10] )[0]
		self.name_off	= unpack("<H", parent.raw[self.offset+10:self.offset+12])[0]
		self.flags 		= parent.raw[self.offset+12:self.offset+14]
		self.unique_ID	= unpack("<H", parent.raw[self.offset+14:self.offset+16])[0]
		self.next 		= self.offset + self.length

		if self.nonresident:
			self.residentStr  = "Non-Resident"
		else:
			self.content_size = unpack("<L", parent.raw[self.offset+16:self.offset+20])[0]
			self.cont_offset  = unpack("<H", parent.raw[self.offset+20:self.offset+22])[0]
			self.residentStr  = "Resident"

		self.attr[self.type_ID]()

		self.print_header()
		self.print_attr[self.type_ID]

		if parent.raw[self.next:self.next+4] != b'\xff\xff\xff\xff':
			parent.add_attribute(MFTAttribute(self.next, self.parent))


	def print_header():
		print("Type: {} ({}) NameLen: ({}) {} size: {}".format(self.type_name, self.type_ID, self.name_len, self.residentStr, self.length))
		if debug:
			if self.nonresident:
				pass
			else:
				print("Offset to content: {}   Size of Content: {}".format(self.cont_offset, self.content_size))
				print()

		

def main():
	global bytes_per_sector, sectors_per_cluster, total_sectors, MFT_start_cluster, size_MFT_entry, size_index_record
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
		total_sectors       = unpack("<Q", fd.read(8))[0]
		MFT_start_cluster   = unpack("<Q", fd.read(8))[0]
		fd.read(8) #(8 bytes) - start cluster of MFT mirror $DATA attribute
		size_MFT_entry      = int(unpack("<b", fd.read(1))[0]) # clusters per file record (MFT entry)
		fd.read(3) #(3 bytes) - unused
		size_index_record   = int(unpack("<B", fd.read(1))[0]) # clusters per index block
		fd.read(3) #(3 bytes) - unused
		fd.read(8) #(8 bytes) - serial number of drive
		
		size_MFT_entry = int(math.pow(2, abs(size_MFT_entry)))
		if debug:
			print("Bytes per sector: {}".format(bytes_per_sector))
			print("MFT start: {}".format(MFT_start_cluster))
			print("Secotrs per cluster: {}".format(sectors_per_cluster))
			print("Size of MFT: {}".format(size_MFT_entry))
			print("Total sectors: {}".format(total_sectors))
			print()
		mft = MFTEntry(MFT_start_cluster, fd)

def usage():
	print("ntfs_mft ")

if __name__ == '__main__':
	try:
		main()
	except:
		traceback.print_tb(sys.exc_info()[2])
		print(sys.exc_info()[1])