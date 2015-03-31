#! /usr/bin/env python3
"""
Author: Zach Greenhalge
Parses the MFT entries in an NTFS system
"""

import sys, math, traceback, time
from struct import unpack

bytes_per_sector    = -1
sectors_per_cluster = -1
total_sectors       = -1
MFT_start_cluster   = -1
size_MFT_entry      = -1
size_index_record   = -1
debug = True

class MFTEntry:
	"""Parses an MFT entry header and creates MFTAttribute instances for all attributes in the entry"""
	printStr = "Sequence: {}\n$LogFile Sequence Number: {}\n{}\nUsed Size: {}\nAllocated Size: {}\n"

	def __init__(self, start, fd):
		self.offset 		= bytes_per_sector * sectors_per_cluster * start
		fd.seek(self.offset, 0)
		print("$MFT starts at: {0:} ({0:X})".format(self.offset))
		self.raw			= fd.read(size_MFT_entry)
		# print(repr(self.raw))

		self.signature   	= bytes.decode(self.raw[0:4]  )    #  signature as string (0-3)
		self.fixup_offset	= unpack("<H", self.raw[4:6]  )[0] #  relative to start of entry (4-5)
		self.fixup_entry 	= unpack("<H", self.raw[6:8]  )[0] # (6-7)
		self.LSN		 	= unpack("<Q", self.raw[8:16] )[0] # (8-15)
		self.seq_value   	= unpack("<H", self.raw[16:18])[0] # (16-17)
		self.link_count		= unpack("<H", self.raw[18:20])[0] # (18-19)
		self.attr_offset	= unpack("<H", self.raw[20:22])[0] # (20-21)
		self.flags			= unpack("<2B", self.raw[22:24])   #  0x01 = in use, 0x02 = directory (22-23)
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
		print(self.printStr.format(self.seq_value, self.LSN, self.flagStr, self.size_used+self.attr_offset, self.allocated_size))

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
		self.new_attribute(self.attr_offset)
		
	def new_attribute(self, offset):
		#both checks probably not necessary...
		if debug:
			print("Attempting to read attribute at offset {}".format(offset))
		if self.raw[offset:offset+4] != b'\xFF\xFF\xFF\xFF':
			if offset + 16 < self.size_used and len(self.attributes) < self.next_att_id:
				# print("(offset+header) {} + 16 < {} (used size) and len(attributes)={} < {} (next attr ID)".format(offset, self.size_used, len(self.attributes), self.next_att_id))
				self.add_attribute(MFTAttribute(offset, self))
			# else:
			# 	print("  (offset+header) {} + 16 > {} (used size) or len(attributes)={} > {} (next attr ID)".format(offset, self.size_used, len(self.attributes), self.next_att_id))
		else:
			print("  First four bytes found: 0x{}".format(hex_from_bytes(self.raw[offset:offset+4])))
			print()
			print("Parsing complete")


	def add_attribute(self, attribute):
		self.attributes.append(attribute)


class MFTAttribute:
	"""Parses an attribute in an MFTEntry"""
	attr_name = {
		16:  "$STANDARD_INFORMATION",
		32:  "$ATTRIBUTE_LIST",
		48:  "$FILE_NAME",
		64:  "$OBJECT_ID",
		80:  "$SECURITY_DESCRIPTOR",
		96:  "$VOLUME_NAME",
		112: "$VOLUME_INFORMATION",
		128: "$DATA",
		144: "$INDEX_ROOT",
		160: "$INDEX_ALLOCATION",
		176: "$BITMAP",
		192: "$REPARSE_POINT",
		256: "$LOGGED_TOOL_STREAM",
	}

	def __init__(self, start, parent):
		self.parent 	= parent
		self.offset 	= start
		
		# Attribute header: first 16 bytes
		self.type_ID	= unpack("<L", parent.raw[self.offset:self.offset+4]    )[0]
		self.length		= unpack("<L", parent.raw[self.offset+4:self.offset+8]  )[0]
		self.nonresident= unpack("<b", parent.raw[self.offset+8:self.offset+9]  )[0]
		self.name_len	= unpack("<b", parent.raw[self.offset+9:self.offset+10] )[0]
		self.name_off	= unpack("<H", parent.raw[self.offset+10:self.offset+12])[0]
		self.flags 		= parent.raw[self.offset+12:self.offset+14]
		self.unique_ID	= unpack("<H", parent.raw[self.offset+14:self.offset+16])[0]
		self.type_name	= self.attr_name[self.type_ID]
		self.next 		= self.offset + self.length

		if self.nonresident:
			self.VCN_start	  = unpack("<Q", parent.raw[self.offset+16:self.offset+24])[0]
			self.VCN_end	  = unpack("<Q", parent.raw[self.offset+24:self.offset+32])[0]
			self.runlist_off  = unpack("<H", parent.raw[self.offset+32:self.offset+34])[0]
			self.compr_unit	  = unpack("<H", parent.raw[self.offset+34:self.offset+36])[0]
			self.content_alloc= unpack("<Q", parent.raw[self.offset+40:self.offset+48])[0]
			self.content_act  = unpack("<Q", parent.raw[self.offset+48:self.offset+56])[0]
			self.content_init = unpack("<Q", parent.raw[self.offset+56:self.offset+64])[0]
			self.residentStr    = "Non-Resident"
			self.print_header()

			self.runlist 	  = []
			self.run_start	  = 0
			if debug:
				print("  RL offset: {}".format(self.runlist_off))
				print("   RL start: {}".format(self.offset+self.runlist_off))
				print("  Runlist is part of: 0x{}".format(hex_from_bytes(parent.raw[self.offset+self.runlist_off:self.offset+self.runlist_off+16])))
			self.rl_header 	  = unpack("<B", parent.raw[self.offset+self.runlist_off:self.offset+self.runlist_off+1])[0]
			self.len_runlen	  = self.rl_header & 0x0F
			self.len_runoff   = (self.rl_header & 0xF0) >> 4
			self.current	  = self.offset + self.runlist_off + 1
			while self.rl_header != 0:
				self.len_runlen	= self.rl_header & 0x0F
				self.len_runoff = (self.rl_header & 0xF0) >> 4
				if debug:
					print("  0x{:X}: Offset: {} Len: {}".format(self.rl_header, self.len_runoff, self.len_runlen))
				self.run_length	= self.getUnsigned(parent.raw[self.current:self.current+self.len_runlen])
				self.current 	= self.current + self.len_runlen
				if debug: 
					print("  Runlist length: {}".format(self.run_length))
				self.run_offset = self.getSigned(parent.raw[self.current:self.current+self.len_runoff])
				self.current	= self.current + self.len_runoff
				if debug:
					print("  Runlist offset: {}".format(self.run_offset))
				self.run_start	= self.run_start + self.run_offset
				if debug:
					print("  Adding to prev offset gives: {}".format(self.run_start))
					print("  Clusters go from {} to {}".format(self.run_start, self.run_start+self.run_length-1))
				for i in range(self.run_start, self.run_start+self.run_length):
					self.runlist.append(i)
				self.rl_header  = unpack("<B", parent.raw[self.current:self.current+1])[0]
				self.current 	= self.current + 1
				if debug:
					print()
		else:
			self.content_size 	= unpack("<L", parent.raw[self.offset+16:self.offset+20])[0]
			self.cont_offset  	= unpack("<H", parent.raw[self.offset+20:self.offset+22])[0]
			self.content_start	= self.offset + self.cont_offset
			self.content 	 	= parent.raw[self.content_start:self.content_start + self.content_size]
			self.residentStr 	= "Resident"
			self.print_header()
			self.attr_setup()

		self.print_attr()

		parent.new_attribute(self.next)


	def print_header(self):
		print("Type: {} ({}) NameLen: ({}) {}   size: {}".format(self.type_name, self.type_ID, self.name_len, self.residentStr, self.length))
		if debug:
			if not self.nonresident:
				print("  Offset to content: {}   Size of Content: {}".format(self.cont_offset, self.content_size))

	def attr_setup(self):
		if   self.type_ID == 16:
			self.temp 			= self.convert_time(unpack("<Q", self.content[ 0: 8])[0])
			self.creation_time	= time.ctime(self.temp)

			self.temp 			= self.convert_time(unpack("<Q", self.content[ 8:16])[0])
			self.file_altered	= time.ctime(self.temp)

			self.temp 			= self.convert_time(unpack("<Q", self.content[16:24])[0])
			self.MFT_altered	= time.ctime(self.temp)

			self.temp 			= self.convert_time(unpack("<Q", self.content[24:32])[0])
			self.file_accessed	= time.ctime(self.temp)

			self.content_flags	= self.get_flags(unpack("<L", self.content[32:36])[0])
			self.max_versions	= unpack("<L", self.content[36:40])[0]
			self.version_num	= unpack("<L", self.content[40:44])[0]
			self.class_ID		= unpack("<L", self.content[44:48])[0]
			self.owner_ID		= unpack("<L", self.content[48:52])[0]
			self.security_ID 	= unpack("<L", self.content[52:56])[0]
			self.quota_charged 	= unpack("<Q", self.content[56:64])[0]
			self.update_seq_num = unpack("<Q", self.content[64:72])[0]
			
		elif self.type_ID == 48:
			self.parent_addr	= self.content[ 0: 8]
			self.dir_seq_num	= unpack("<H", self.parent_addr[0:2])[0]
			self.dir_MFT_entry 	= self.getUnsigned(self.parent_addr[2:8])
			self.temp 			= self.convert_time(unpack("<Q", self.content[ 8:16])[0])
			self.date_created	= time.ctime(self.temp)
			self.temp 			= self.convert_time(unpack("<Q", self.content[16:24])[0])
			self.date_modified	= time.ctime(self.temp)
			self.temp 			= self.convert_time(unpack("<Q", self.content[24:32])[0])
			self.MFT_altered 	= time.ctime(self.temp)
			self.temp 		 	= self.convert_time(unpack("<Q", self.content[32:40])[0])
			self.file_accessed 	= time.ctime(self.temp)
			self.alloc_size 	= unpack("<Q", self.content[40:48])[0]
			self.actual_size 	= unpack("<Q", self.content[48:56])[0]
			self.content_flags 	= self.get_flags(unpack("<L", self.content[56:60])[0])
			self.reparse_val 	= unpack("<L", self.content[60:64])[0]
			self.file_name_len  = unpack("<B", self.content[64:65])[0]
			self.file_namespace = unpack("<B", self.content[65:66])[0]
			self.file_name 		= bytes.decode(self.content[66:66+(self.file_name_len*2)], encoding="utf-16")

		elif self.type_ID == 128:
			#$DATA
			pass
		#ALL OTHER TYPES NOT SUPPORTED FOR THIS ASSIGNMENT

	def print_attr(self):
		attrStr = "{:>30}  {}"
		if self.nonresident:
			if len(self.runlist) > 100:
				print("  Runlist length: {}".format(len(self.runlist)))
			else:
				print("  Runlist: {}".format(self.runlist))
		elif self.type_ID == 16:
			print(attrStr.format("File creation", self.creation_time))
			print(attrStr.format("File accessed", self.file_accessed))
			print(attrStr.format("File altered", self.file_altered))
			print(attrStr.format("MFT altered", self.MFT_altered))
			print(attrStr.format("Max # versions", self.max_versions))
			print(attrStr.format("Version #", self.version_num))
			print(attrStr.format("Class ID", self.class_ID))
			print(attrStr.format("Owner ID", self.owner_ID))
			print(attrStr.format("Security ID", self.security_ID))
			print(attrStr.format("Quota Charged", self.quota_charged))
			print(attrStr.format("Update seq #", self.update_seq_num))
			print(attrStr.format("Flags", self.content_flags))
		elif self.type_ID == 48:
			print(attrStr.format("Parent dir (MFT#, seq#)", (self.dir_MFT_entry, self.dir_seq_num)))
			print(attrStr.format("File created", self.date_created))
			print(attrStr.format("File modified", self.date_modified))
			print(attrStr.format("File accessed", self.file_accessed))
			print(attrStr.format("MFT altered", self.MFT_altered))
			print(attrStr.format("Allocated size", self.alloc_size))
			print(attrStr.format("Actual size", self.actual_size))
			print(attrStr.format("Flags", self.content_flags))
			print(attrStr.format("Reparse value", self.reparse_val))
			print(attrStr.format("Length of name", self.file_name_len))
			print(attrStr.format("Namespace", self.file_namespace))
			print(attrStr.format("Name", self.file_name))
		elif self.type_ID == 128:
			#$DATA
			pass
		else:
			print("    (unparsed attribute)")
		print()
		print('-'*75)
		print()
	
	def get_flags(self, bites):
		ret = []
		if bites & 0x0001:
			ret.append("Read only")
		if bites & 0x0002:
			ret.append("Hidden")
		if bites & 0x0004:
			ret.append("System")
		if bites & 0x0020:
			ret.append("Archive")
		if bites & 0x0040:
			ret.append("Device")
		if bites & 0x0080:
			ret.append("Normal")
		if bites & 0x0100:
			ret.append("Temporary")
		if bites & 0x0200:
			ret.append("Sparse File")
		if bites & 0x0400:
			ret.append("Reparse Point")
		if bites & 0x0800:
			ret.append("Compressed")
		if bites & 0x1000:
			ret.append("Offline")
		if bites & 0x2000:
			ret.append("Not Indexed")
		if bites & 0x4000:
			ret.append("Encrypted")
		return ", ".join(ret)

	def convert_time(self, windows_time):
		time_to_epoch 	= 116444736000000000
		denominator		= 10000000
		return int((windows_time - time_to_epoch) / denominator)

	def getUnsigned(self, bites):
		num = len(bites)
		while ((num & (num - 1)) != 0) or num < 2:
			bites = bites + b'\x00'
			num = len(bites)
		if len(bites) == 2:
			return unpack("<H", bites)[0]
		if len(bites) == 4:
			return unpack("<L", bites)[0]
		if len(bites) == 8:
			return unpack("<Q", bites)[0]
		raise Exception("Invalid byte len result: {} {}".format(len(bites), bites))

	def getSigned(self, bites):
			#assumes little endian
			if len(bites) == 0:
				raise Exception("0 bytes received...")
			if len(bites) > 8:
				raise Exception("Expected 8 bytes, got {}".format(len(bites)))
			elif len(bites) < 8:
				if bites[-1] >> 7 == 1:
					pad = b'\xFF'
				else:
					pad = b'\x00'
				padLength = 8-len(bites)
			return unpack("<q", bites + (pad * padLength))[0]

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
		size_MFT_entry      = unpack("<b", fd.read(1))[0] # clusters per file record (MFT entry)
		fd.read(3) #(3 bytes) - unused
		size_index_record   = unpack("<B", fd.read(1))[0] # clusters per index block
		fd.read(3) #(3 bytes) - unused
		fd.read(8) #(8 bytes) - serial number of drive
		
		if size_MFT_entry < 0:
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
	print("ntfs_mft")

def hex_from_bytes(data):
	return "".join("{:02X}".format(i) for i in data)

if __name__ == '__main__':
	try:
		main()
	except:
		traceback.print_tb(sys.exc_info()[2])
		print(sys.exc_info()[1])