#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
import math
import zlib

img = {'header': b'\x89PNG\r\n\x1a\n'}


class Unbuffered(object):

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)


class _Getch:

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchUnix:

    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:

    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def putchar(n):
    print(chr(n), end='')


def giveSymb(symbol):
    if ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 0:
        return(">")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 1:
        return("<")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 2:
        return("+")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 3:
        return("-")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 4:
        return(".")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 5:
        return(",")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 6:
        return("[")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 7:
        return("]")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 8:
        return("P")
    elif ((symbol[0] * (65536) + symbol[1] * (256) + symbol[2]) % 11) == 9:
        return("L")
    else:
        return("X")


def load_png_image(image):
    head = image.read(8)
    assert head == b'\x89PNG\r\n\x1a\n', 'File is not PNG image'
    image.seek(4, 1)
    image.seek(4, 1)
    width = int.from_bytes(image.read(4), 'big')
    height = int.from_bytes(image.read(4), 'big')
    image.read(1)
    clmode = int.from_bytes(image.read(1), 'big')
    return width, height, clmode


def plus(a, b):
    return ((a[0] + b[0]) % 256, (a[1] + b[1]) % 256, (a[2] + b[2]) % 256)


def paeth_predictor(a, b, c):
    res = tuple()
    for i in range(0, 3):
        p = (a[i] + b[i] - c[i])
        pa = abs(p - a[i])
        pb = abs(p - b[i])
        pc = abs(p - c[i])
        if (pa <= pb and pa <= pc):
            res += (a[i], )
        elif (pb <= pc):
            res += (b[i], )
        else:
            res += (c[i], )
    return res


def load_png_data(image, image_properties):
    width = image_properties[0]
    height = image_properties[1]
    clmode = image_properties[2]
    if clmode == 6:
        mode = 4
    elif clmode == 2:
        mode = 3
    image.seek(8 + 8 + 13 + 4, 0)

    j = 0
    sz = 0
    pc = b''
    while 1:
        data_size = int.from_bytes(image.read(4), 'big')
        cosi = image.read(4)
        if cosi == b'IEND':
            break
        elif cosi != b'IDAT':
            image.seek(data_size + 4, 1)
            continue
        pc += (image.read(data_size))
        image.seek(4, 1)
        sz += data_size + 4
    data = zlib.decompress(pc)
    pixels = []
    p = 0
    for row_index in range(height):
        filr = data[p]
        p += 1
        row = []
        left_pixel = (0, 0, 0)
        upleft_pixel = (0, 0, 0)
        for pixel in range(0, width):
            r = data[p]
            g = data[p + 1]
            b = data[p + 2]
            pxl = (r, g, b)
            p += mode
            if filr == 0:
                left_pixel = pxl
                row.append(pxl)
            elif filr == 1:
                left_pixel = plus(left_pixel, pxl)
                row.append(left_pixel)
            elif filr == 2:
                left_pixel = plus(pxl, pixels[len(pixels)-1][pixel])
                row.append(left_pixel)
            elif filr == 4:
                up_pixel = pixels[len(pixels)-1][pixel]
                current = plus(pxl,
                               paeth_predictor(left_pixel,
                                               up_pixel,
                                               upleft_pixel))
                row.append(current)
                left_pixel = current
                upleft_pixel = up_pixel
        pixels.append(row)
    return pixels


def isPng(inp):
    header = b'\x89PNG\r\n\x1a\n'
    if inp == header:
        return 1
    else:
        return 0

parser = OptionParser(usage="usage: %prog [options] files",
                      version="%prog 0.1")
parser.add_option("-i",
                  "--FileInput",
                  action="store",
                  dest="filinp",
                  type="string",
                  help="Nastaveni jmena vstupniho souboru")
parser.add_option("-o",
                  "--FileOutput",
                  action="store",
                  dest="filout",
                  type="string",
                  help="Nastaveni jmena vystupniho souboru")

args = sys.argv[1:]
(options, args) = parser.parse_args()
if options.filinp:
    if not (os.path.exists(options.filinp)):
        print("Soubor neexistuje")
        exit(2)
if options.filout is None:
    print("Výstup není definován")
    exit(2)
if options.filinp is None:
    print("Vstup není definován")
    exit(2)

matr = []
j = 0
maxx = 0
maxy = 0
with open(options.filinp, 'rb') as f:
    image_properties = load_png_image(f)
    pixels = load_png_data(f, image_properties)
    for it in pixels:
        matr.append([])
        maxy = len(it)
        for i in it:
            matr[j].append(giveSymb(i))
        j += 1
maxx = j


class Patf:

    x = 0
    y = 0
    v = 0

    def turnLeft(self):
        self.v = (self.v - 1) % 4
        self.step()

    def turnRight(self):
        self.v = (self.v + 1) % 4
        self.step()

    def step(self):
        if self.v == 0:
            self.x += 1
        elif self.v == 1:
            self.y += 1
        elif self.v == 2:
            self.x -= 1
        elif self.v == 3:
            self.y -= 1

    def swVec(self):
        if self.v == 0:
            self.v = 2
        elif self.v == 1:
            self.v = 3
        elif self.v == 2:
            self.v = 0
        elif self.v == 3:
            self.v = 1


ch = Patf()
bftxt = ""
# 0 ->
# 1 dolu
# 2 <-
# 3 nahoru
tape = [0]
brstx = []
brsty = []
tapepnt = 0
o = 1

x = 0
y = 0
outstr = ""
while maxx > y and maxy > x and y >= 0 and x >= 0:
    if matr[y][x] == "P":
        ch.turnRight()
    elif matr[y][x] == "L":
        ch.turnLeft()
    elif matr[y][x] == "X":
        ch.step()
    else:
        outstr += matr[y][x]
        ch.step()
    x = ch.x
    y = ch.y

istr = outstr

i = 0
outr = ""
while i < len(istr):
    if istr[i] == "<" \
       or istr[i] == ">" \
       or istr[i] == "+" \
       or istr[i] == "-" \
       or istr[i] == "." \
       or istr[i] == "," \
       or istr[i] == "[" \
       or istr[i] == "]":
        outr += istr[i]
    i += 1
istr = outr

sd = math.ceil(math.sqrt(len(istr))) + 1
r = 0
p = 0
rst = ""
sud = 0
tmp = ""
i = 0
while i < (sd * sd):
    if r == 0:
        if i < sd:
            if p >= len(istr):
                rst += "X"
            else:
                if istr[p] != '\n':
                    rst += istr[p]
                    p += 1
                else:
                    p += 1
        elif i == sd:
            if p >= len(istr):
                rst += "X"
            else:
                if sud == 1:
                    tmp = rst[-(sd-1):][::-1]
                    istr = istr[0:-(sd-1)] + tmp
                rst += "P\nL"
                r += 1
                sud = 1
    else:
        if math.fmod(i, sd + 1) == sd - 1:
            if p >= len(istr):
                rst += "X"
            else:
                if sud == 1:
                    tmp = rst[-(sd - 1):][::-1]
                    rst = rst[0:-(sd - 1)] + tmp
                if p < len(istr):
                    rst += "P\nL"
                if sud == 0:
                    sud = 1
                else:
                    sud = 0
        elif math.fmod(i, sd + 1) < sd:
            if p >= len(istr):
                rst += "X"
            else:
                if istr[p] != '\n':
                    rst += istr[p]
                    p += 1
                else:
                    p += 1
    i += 1
if sud == 1:
    tmp = rst[-(sd+1):][::-1]
    rst = rst[0:-(sd+1)] + tmp
    rst = rst[:-1] + 'P'
rst += '\n'


j = 0
i = 0
s = 0
size = sd+1
pixels = []
line = []
while s < len(rst):
    if rst[s] == ">":
        r = 255
        g = 0
        b = 0
    elif rst[s] == "<":
        r = 128
        b = 0
        g = 0
    elif rst[s] == "+":
        r = 0
        g = 255
        b = 0
    elif rst[s] == "-":
        r = 0
        g = 128
        b = 0
    elif rst[s] == ".":
        r = 0
        g = 0
        b = 255
    elif rst[s] == ",":
        r = 0
        g = 0
        b = 128
    elif rst[s] == "[":
        r = 255
        g = 255
        b = 0
    elif rst[s] == "]":
        r = 128
        g = 128
        b = 0
    elif rst[s] == "P":
        r = 0
        g = 255
        b = 255
    elif rst[s] == "L":
        r = 0
        g = 128
        b = 128
    elif rst[s] == "X":
        r = 0
        g = 0
        b = 0
    elif rst[s] == "\n":
        pixels.append(line)
        line = []
        s += 1
        continue
    else:
        r = 0
        g = 0
        b = 0
    a = 255
    s += 1
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


tmp = b''
idat_data = b''
for line in img['IDAT']:
    idat_data += bytes([line[0]])
    for value in line[1]:
        tmp += bytes(value)
    idat_data += tmp
    tmp = b''

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
