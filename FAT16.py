#!/usr/bin/env python3
"""
Author: Zach Greenhalge
A tool to parse the values of a FAT16 boot table
"""

import sys, math
from struct import unpack

def main(offset, filename):
	offset = int(offset)
	try:
		with open(filename, 'rb') as fd:
			fd.seek(offset)
			fd.read(3) #3 bytes => jump to bootstrap code
			oem_name         = bytes.decode(fd.read(8)) #name of formatting OS
			bytes_per_sector = unpack("<H", fd.read(2))[0] 
			sector_per_clust = unpack("<b", fd.read(1))[0]
			reserved_sectors = unpack("<H", fd.read(2))[0]
			num_FAT_copies   = unpack("<b", fd.read(1))[0] 
			max_root_entries = unpack("<H", fd.read(2))[0]
			small_num_sectors= unpack("<H", fd.read(2))[0] 
			fd.read(1) #1 byte  => media descriptor
			sectors_per_FAT  = unpack( "<H", fd.read(2))[0]
			fd.read(2) #2 bytes => sectors per track
			fd.read(2) #2 bytes => number of heads
			fd.read(4) #4 bytes => hidden sctors
			large_num_sectors= unpack( "<I", fd.read(4))[0]
			fd.read(1) #1 byte  => drive number
			fd.read(1) #1 byte  => reserved byte
			fd.read(1) #1 byte  => extended boot signature
			vol_serial_number = unpack("<4s", fd.read(4))[0][::-1]
			volume_label      = bytes.decode(fd.read(11))
			file_system_type  = bytes.decode(fd.read(8))
			fd.seek(448, 1) #skip boot code
			boot_signature    = fd.read(2) #should be 0xAA55
			clust_size  = bytes_per_sector*sector_per_clust
			if small_num_sectors == 0:
				sectors = int(large_num_sectors)
			else:
				sectors = int(small_num_sectors)
			final_sector = sectors+offset-1
			final_in_img = final_sector - (sectors % sector_per_clust)
			# if boot_signature != 0xAA55:
			# 	print("FAT format incorrect - final signature is {!r}".format(boot_signature))
			# 	print("expect: 0xAA55")
			# 	sys.exit(0)
			print("FILE SYSTEM INFORMATION")
			print()
			print('-'*40)
			print("File System Type: FAT16")
			print()
			print("OEM Name:", oem_name)
			print("Volume ID:", vol_serial_number)
			print("Volume Label (Boot Sector):", volume_label)
			print()
			print("File System Type Label:", file_system_type)
			print()
			print("File System Layout (in sectors)")
			print("Total Range:", offset, "-", final_sector)
			print("Total Range in Image:", offset, '-', final_in_img)
			print("* Reserved:", offset, '-', reserved_sectors+offset-1)
			print("** Boot Sector:", offset)
			FAT_print = 0
			FAT_start = reserved_sectors+offset
			while num_FAT_copies - FAT_print > 0:
				print("* FAT {}: {} - {}".format(FAT_print, FAT_start, FAT_start+sectors_per_FAT-1))
				FAT_start = FAT_start + sectors_per_FAT
				FAT_print += 1
			data_start  = FAT_start
			root_start  = FAT_start
			root_size   = int(math.ceil((max_root_entries*32)/bytes_per_sector))
			data_size   = sectors - (reserved_sectors+offset) + (sectors_per_FAT*num_FAT_copies) + root_size
			clust_start = root_start + root_size
			extra_sector= ((sectors+offset)-data_start) % sector_per_clust
			clusterEnd  = int(math.ceil((sectors-clust_start+1)/sector_per_clust))
			print("* Data Area:", data_start, '-', final_sector)
			print("** Root Directory:", root_start, '-', root_start+root_size-1)
			print("** Cluster Area:", clust_start, '-', final_sector-extra_sector)
			print("** Non-clustered:", final_sector-extra_sector+1, '-', final_sector)
			print()
			print("CONTENT INFORMATION")
			print('-'*40)
			print("Sector Size:", bytes_per_sector, "bytes")
			print("Cluster Size:", clust_size, "bytes")
			print("Total Cluster Range:", 2, '-', clusterEnd)
	except Exception as e:
		print(sys.exc_info()[0:1])
		raise e

def dataFromBytes(fmt, components, bytestr):
	"""Takes a bytestr and returns it in the specified format"""
	ret = bytestr
	if   fmt == 1: #byte
		ret = unpack(">{:}B".format(len(bytestr)), bytestr)[0]
	elif fmt == 2: #ASCII string
		ret = bytes.decode(bytestr)
	elif fmt == 3: #short
		ret = unpack(">{:}H".format(components), bytestr)[0]
	elif fmt == 4: #long
		ret = unpack(">{:}L".format(components), bytestr)[0]
	elif fmt == 5: #rational
		ret = unpackRational(components, bytestr)
	elif fmt == 7: #raw data
		ret = "".join(*unpack(">{:}B".format(components), bytestr))
	return ret

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])