#!/usr/bin/env python3
"""
Author: Zach Greenhalge
A program that parses EXIF markers from a JPEG
"""

import sys, codecs
from struct import unpack

TAGS={      0x100:  "ImageWidth",
	        0x101:  "ImageLength",
	        0x102:  "BitsPerSample",
	        0x103:  "Compression",
	        0x106:  "PhotometricInterpretation",
	        0x10A:  "FillOrder",
	        0x10D:  "DocumentName",
	        0x10E:  "ImageDescription",
	        0x10F:  "Make",
	        0x110:  "Model",
	        0x111:  "StripOffsets",
	        0x112:  "Orientation",
	        0x115:  "SamplesPerPixel",
	        0x116:  "RowsPerStrip",
	        0x117:  "StripByteCounts",
	        0x11A:  "XResolution",
	        0x11B:  "YResolution",
	        0x11C:  "PlanarConfiguration",
	        0x128:  "ResolutionUnit",
	        0x12D:  "TransferFunction",
	        0x131:  "Software",
	        0x132:  "DateTime",
	        0x13B:  "Artist",
	        0x13E:  "WhitePoint",
	        0x13F:  "PrimaryChromaticities",
	        0x156:  "TransferRange",
	        0x200:  "JPEGProc",
	        0x201:  "JPEGInterchangeFormat",
	        0x202:  "JPEGInterchangeFormatLength",
	        0x211:  "YCbCrCoefficients",
	        0x212:  "YCbCrSubSampling",
	        0x213:  "YCbCrPositioning",
	        0x214:  "ReferenceBlackWhite",
	        0x828F: "BatteryLevel",
	        0x8298: "Copyright",
	        0x829A: "ExposureTime",
	        0x829D: "FNumber",
	        0x83BB: "IPTC/NAA",
	        0x8769: "ExifIFDPointer",
	        0x8773: "InterColorProfile",
	        0x8822: "ExposureProgram",
	        0x8824: "SpectralSensitivity",
	        0x8825: "GPSInfoIFDPointer",
	        0x8827: "ISOSpeedRatings",
	        0x8828: "OECF",
	        0x9000: "ExifVersion",
	        0x9003: "DateTimeOriginal",
	        0x9004: "DateTimeDigitized",
	        0x9101: "ComponentsConfiguration",
	        0x9102: "CompressedBitsPerPixel",
	        0x9201: "ShutterSpeedValue",
	        0x9202: "ApertureValue",
	        0x9203: "BrightnessValue",
	        0x9204: "ExposureBiasValue",
	        0x9205: "MaxApertureValue",
	        0x9206: "SubjectDistance",
	        0x9207: "MeteringMode",
	        0x9208: "LightSource",
	        0x9209: "Flash",
	        0x920A: "FocalLength",
	        0x9214: "SubjectArea",
	        0x927C: "MakerNote",
	        0x9286: "UserComment",
	        0x9290: "SubSecTime",
	        0x9291: "SubSecTimeOriginal",
	        0x9292: "SubSecTimeDigitized",
	        0xA000: "FlashPixVersion",
	        0xA001: "ColorSpace",
	        0xA002: "PixelXDimension",
	        0xA003: "PixelYDimension",
	        0xA004: "RelatedSoundFile",
	        0xA005: "InteroperabilityIFDPointer",
	        0xA20B: "FlashEnergy",                  # 0x920B in TIFF/EP
	        0xA20C: "SpatialFrequencyResponse",     # 0x920C    -  -
	        0xA20E: "FocalPlaneXResolution",        # 0x920E    -  -
	        0xA20F: "FocalPlaneYResolution",        # 0x920F    -  -
	        0xA210: "FocalPlaneResolutionUnit",     # 0x9210    -  -
	        0xA214: "SubjectLocation",              # 0x9214    -  -
	        0xA215: "ExposureIndex",                # 0x9215    -  -
	        0xA217: "SensingMethod",                # 0x9217    -  -
	        0xA300: "FileSource",
	        0xA301: "SceneType",
	        0xA302: "CFAPattern",                   # 0x828E in TIFF/EP
	        0xA401: "CustomRendered",
	        0xA402: "ExposureMode",
	        0xA403: "WhiteBalance",
	        0xA404: "DigitalZoomRatio",
	        0xA405: "FocalLengthIn35mmFilm",
	        0xA406: "SceneCaptureType",
	        0xA407: "GainControl",
	        0xA408: "Contrast",
	        0xA409: "Saturation",
	        0xA40A: "Sharpness",
	        0xA40B: "DeviceSettingDescription",
	        0xA40C: "SubjectDistanceRange",
	        0xA420: "ImageUniqueID",
	        0xA432: "LensSpecification",
	        0xA433: "LensMake",
	        0xA434: "LensModel",
	        0xA435: "LensSerialNumber"
}

typeLength=[0,1,1,2,4,8,1,1,2,4,8,4,8]

class IFDEntry:
	"""A container class for all data relevant to an IFD entry"""
	printStr = "{:>5s} {:20s} {}"
	def __init__(self, fd, offsetStart):
		self.location   = fd.tell()
		self.tag        = unpack(">H", fd.read(2))[0]
		self.name       = TAGS[int("{:d}".format(self.tag))]
		self.format     = unpack(">H", fd.read(2))[0]
		self.components = unpack(">L", fd.read(4))[0]
		self.dataLength = typeLength[self.format] * self.components
		if self.dataLength > 4:
			self.offset = unpack(">L", fd.read(4))[0]
			fd.seek(offsetStart+self.offset)
			self.data   = fd.read(self.dataLength)
		else:
			self.offset = 0
			self.data   = fd.read(self.dataLength)
		self.data       = dataFromBytes(self.format, self.components, bytes(self.data))

		fd.seek(self.location+12)
		print(self.printStr.format("{:x}".format(self.tag), self.name, self.data))

class IFD:
	"""Basically just a list of IFDEntry"""
	def __init__(self, fd, offset):
		self.entrynum = unpack(">H", fd.read(2))[0]
		self.entries = []
		print("Number of IFD Entries:", self.entrynum)
		while len(self.entries) < self.entrynum:
			self.entries.append(IFDEntry(fd, offset))



class App:
	"""A container class for all data relevant to an App"""
	printStr = "[0x{:04X}] Marker 0x{:04X} size=0x{:04X}"
	def __init__(self, marker, fd):
		"""Extract the data for the app from the marker and file descriptor"""
		if marker == b'\xFF\xDA': #image data header
			self.marker = unpack(">H", marker)[0]
			self.size = unpack(">H", fd.read(2))[0]
			self.location = fd.tell() - 2
			self.next = self.size + self.location + 2
			print(self.printStr.format(self.location, self.marker, self.size))
			sys.exit(0)
		if marker[0] != 0xFF: #All headers are two bytes, starting with 0xFF
			print("Invalid marker found.", marker, "Exiting.")
			sys.exit(1)
		self.marker   = unpack(">H", marker)[0]
		self.size     = unpack(">H", fd.read(2))[0]
		self.location = fd.tell() - 4
		self.next     = self.size + self.location + 2
		self.name     = unpack(">6s", fd.read(6))[0].strip(b'\x00')
		print(self.printStr.format(self.location, self.marker, self.size))
		if checkforExif():
			self.IFD = IFD(fd, self.location+10)
		fd.seek(self.next)

	def checkforExif():
		"""Returns true if this app is the Exif data. Can exit the program if an error is detected"""
		if self.name == b'Exif':
			temp = fd.read(2)
			if temp != b'MM':
				print("Little endian format found. Exiting.")
				sys.exit(1)
			temp = fd.read(2)
			if temp != b'\x00\x2A':
				print("Incorrect format of marker", self.name, "Exiting.")
				sys.exit(1)
			self.offset = unpack(">L", fd.read(4))[0]
			if self.offset != fd.tell() - self.location - 10: #location - start - 10 bytes to first M
				print("Incorect IFD offset in marker", self.name)
				print("Was", fd.tell() - self.location - 10, "expected", self.offset)
				sys.exit(1)
			return True
		return False

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

def unpackRational(components, bytestr):
	"""Unpacks a given number of rationals from the bytestr"""
	ret = []
	size = len(ret)
	while size <= components:
		string = bytestr[size:size+8]
		if len(string) >= 8:
			ret.append("{}/{}".format(*unpack(">LL", string)))
		size += 8
	return ret

def main(args):
	"""Checks if the file passed is a JPEG, and reads in all JPEG apps if it is"""
	if len(args) != 1:
		usage()
		sys.exit(2)
	apps = []
	with open(args[0], "rb") as fd:
		if unpack(">H", fd.read(2))[0] != 0xFFD8:
			print("File passed is not a JPEG")
			sys.exit(1)
		marker = fd.read(2)
		while marker != b'\xFF\xD9': #0xFFD9 == EOF in JPEG
			apps.append(App(marker, fd))
			marker = fd.read(2)

def usage():
	print("exif <file>")

if __name__ == '__main__':
	main(sys.argv[1:])