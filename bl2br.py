#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
import zlib

def load_png_image(image):
    """Return width and height of PNG image

    Args:
        image: reference to PNG file
    Returns:
        (width, height) tuple
    """

    # precte hlavicku obrazku
    head = image.read(8)
    # zkontroluje, ze se jedna o hlavicku PNG obrazku
    assert head == b'\x89PNG\r\n\x1a\n', 'File is not PNG image'

    image.seek(4, 1)  # preskoci IHDR SIZE
    image.seek(4, 1)  # preskoci IHDR TYPE
    # precte sirku obrazku z IHDR data
    width = int.from_bytes(image.read(4), 'big')
    # precte vysku obrazku z IHDR data
    height = int.from_bytes(image.read(4), 'big')

    return width, height

def load_png_data(image, image_properties):
    """Return PNG image pixels

    Args:
        image: reference to PNG file
        image_properties: (width, height) tuple
    Returns:
        list of list of pixels - [[(r, g, b, a), (r, g, b, a) ...]]
    """

    width = image_properties[0]
    height = image_properties[1]
    # preskoci hlavicku obrazku a oznaceni IHDR - 0 znamena, ze se pozice kurzoru nastavuje od zacatku
    image.seek(8 + 8 + 13 + 4, 0)
    # nacte delku dat IDAT chunku
    data_size = int.from_bytes(image.read(4), 'big')
    # preskoci oznaceni chunku b'IDAT'
    image.seek(4, 1)
    # nacte data
    data = image.read(data_size)
    # rozbali data v chunku IDAT
    data = zlib.decompress(data)

    # do seznamu pixels se nactou vsechny radky obrazku
    pixels = []
    for row_index in range(height):
        # do seznamu row se ukladaji jednotlive entice
        # obsahujici podslozky pixelu - r, g, b, alpha channel
        row = []
        # nastaveni pozice na zacatek dalsiho radku
        # kazdy pixel se sklada ze 4 bytu - proto ta ctyrka
        # kazdy radek obsahuje na zacatek typ filtrovani
        # a ten musime preskocit pomoci "+ row_index"
        start = row_index * width * 4 + row_index
        # konec je delka radku + "pocatecni pozice"
        end = start + width * 4
        # inkrementuje se s krokem 4 - pixel obsahuje 4 byty
        for pixel in range(start, end, 4):
            r = data[pixel + 1]
            g = data[pixel + 2]
            b = data[pixel + 3]
            a = data[pixel + 4]
            row.append((r, g, b, a))
        pixels.append(row)
    return pixels


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
	print("Usage: inter_bl.by -f file.png")
	exit(2);

i=0
hd=b'';
chunk=b'';
pr=0
with open(options.filename, 'rb') as f:
	image_properties = load_png_image(f)
	pixels = load_png_data(f, image_properties)
	for it in pixels:
		for i in it:
			print(i)
	print()












