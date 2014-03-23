#!/usr/bin/python3
import sys
from optparse import OptionParser
import os

def isPng(inp):
	header = b'\x89PNG\r\n\x1a\n'
	if inp == header:
		return 1
	else:
		return 0

#Parsovani a nacitani
parser = OptionParser(usage="Usage: %prog -f file", version="%prog 0.1")
parser.add_option("-f","--FileName", action="store", dest="filename", type="string", help="Nastaveni jmena vstupniho souboru")

args = sys.argv[1:]
(options, args) = parser.parse_args()
if options.filename:
	if not (os.path.exists(options.filename)):
		print("Soubor neexistuje")
else:
	print("Usage: inter_bl.by -f file")
	exit(2);

i=0
hd=b'';
chunk=b'';
pr=0
with open(options.filename, 'rb') as f:
	while 1:
		byte = f.read(1)
		if not byte:
			break
		if i < 8:
			hd=hd+byte
		elif i == 8:
			if isPng(hd) != 1:
				exit(2)
		i+=1	
		if i < 8:
			chunk=chunk+byte
			if chunk == b'IDAT':
				pr=1
		if pr == 1:
			print(hex(byte))

