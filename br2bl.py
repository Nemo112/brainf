#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
import math
import zlib

img = {'header': b'\x89PNG\r\n\x1a\n'}
o=1
istr=""
parser = OptionParser(usage="usage: %prog [options] files", version="%prog 0.1")
parser.add_option("-i","--FileInput", action="store", dest="filinp", type="string", help="Nastaveni jmena vstupniho souboru")
parser.add_option("-o","--FileOutput", action="store", dest="filout", type="string", help="Nastaveni jmena vystupniho souboru")

args = sys.argv[1:]
(options, args) = parser.parse_args()
if options.filinp:
	if os.path.exists(options.filinp):
		with open(options.filinp, mode='r', encoding='utf-8') as stream:
			for intp in stream.readlines():
				istr=istr+intp
	else:
		print("Soubor neexistuje")
		exit(2)
else:
	istr = input()
if not options.filout:
	print("Zadejte výstupní soubor")
	exit(2)
sd=math.ceil(math.sqrt(len(istr)))+1
i=0 
r=0 
p=0 
rst=""
sud=0
tmp=""
i=0
while i < (sd*sd):
	if r == 0:
		if i < sd:
			if p >= len(istr):
				rst+="X"
			else:
				if istr[p] != '\n':
					rst+=istr[p]
					p+=1
				else:
					p+=1
		elif i == sd:
			if p >= len(istr):
				rst+="X"
			else:
				if sud == 1:
					tmp=rst[-(sd-1):][::-1]
					istr=istr[0:-(sd-1)]+tmp
				rst+="P\nL"
				r+=1
				sud=1
	else:		
		if math.fmod(i,sd+1) == sd-1:
			if p >= len(istr):
				rst+="X"
			else:
				if sud == 1:
					tmp=rst[-(sd-1):][::-1]
					rst=rst[0:-(sd-1)]+tmp
				if p < len(istr):
					rst+="P\nL"
				if sud == 0:
					sud=1
				else:
					sud=0
		elif math.fmod(i,sd+1) < sd:
			if p >= len(istr):
				rst+="X"
			else:
				if istr[p] != '\n':
					rst+=istr[p]
					p+=1
				else:
					p+=1 
	i+=1
if sud == 1:
	tmp=rst[-(sd+1):][::-1]
	rst=rst[0:-(sd+1)]+tmp
	rst=rst[:-1]+'P'
rst+='\n'
j=0
i=0
s=0
size = sd+1
pixels = []
line=[]
while s < len(rst):
	if rst[s] == ">" :
		r = 255
		g = 0
		b = 0
	elif rst[s] == "<" :
		r = 128
		b = 0
		g = 0
	elif rst[s] == "+" :
		r = 0
		g = 255
		b = 0
	elif rst[s] == "-" :
		r = 0
		g = 128
		b = 0
	elif rst[s] == "." :
		r = 0
		g = 0
		b = 255
	elif rst[s] == "," :
		r = 0
		g = 0
		b = 128
	elif rst[s] == "[" :
		r = 255
		g = 255
		b = 0
	elif rst[s] == "]" :
		r = 128
		g = 128
		b = 0
	elif rst[s] == "P" :
		r = 0
		g = 255
		b = 255
	elif rst[s] == "L" :
		r = 0
		g = 128
		b = 128
	elif rst[s] == "X" :
		r = 0
		g = 0
		b = 0
	elif rst[s] == "\n" :
		pixels.append(line)
		line=[]
		s+=1
		continue
	else:
		r = 0
		g = 0
		b = 0
	a = 255
	s+=1
	line.append((r, g, b, a))

img['IDAT'] = [(0, x) for x in pixels]


img['IHDR'] = {
	'width': len(pixels[0]).to_bytes(4, 'big'),
	'height': len(pixels).to_bytes(4, 'big'),
	'bit depth': bytes([8]),
	'colour type': bytes([6]),
	'compression method': bytes([0]),
	'filter method': bytes([0]),
	'interlace method': bytes([0]),
}

hdr_data = img['IHDR']
ihdr_data = hdr_data['width'] + \
			hdr_data['height'] + \
			hdr_data['bit depth'] + \
			hdr_data['colour type'] + \
			hdr_data['compression method'] + \
			hdr_data['filter method'] + \
			hdr_data['interlace method']

ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data).to_bytes(4, 'big')

ihdr_size = len(ihdr_data).to_bytes(4, 'big')

i=0
idat_data = b''
for line in img['IDAT']:
	idat_data += bytes([line[0]])
	for value in line[1]:
		idat_data += bytes(value)
		i+=1

idat_data = zlib.compress(idat_data)
idat_crc = zlib.crc32(b'IDAT' + idat_data).to_bytes(4, 'big')
idat_size = len(idat_data).to_bytes(4, 'big')

ihdr = ihdr_size + b'IHDR' + ihdr_data + ihdr_crc
idat = idat_size + b'IDAT' + idat_data + idat_crc
iend = bytes(4) + b'IEND' + b'' + zlib.crc32(b'IEND').to_bytes(4, 'big')
data = img['header'] + ihdr + idat + iend

try:
	f = open(options.filout, "wb")
	try:
		f.write(data)
	finally:
		f.close()
except IOError:
	pass
