#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
import zlib


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
    if symbol == (255, 0, 0):
        return(">")
    elif symbol == (128, 0, 0):
        return("<")
    elif symbol == (0, 255, 0):
        return("+")
    elif symbol == (0, 128, 0):
        return("-")
    elif symbol == (0, 0, 255):
        return(".")
    elif symbol == (0, 0, 128):
        return(",")
    elif symbol == (255, 255, 0):
        return("[")
    elif symbol == (128, 128, 0):
        return("]")
    elif symbol == (0, 255, 255):
        return("P")
    elif symbol == (0, 128, 128):
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
            image.seek(data_size+4, 1)
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
                left_pixel = plus(pxl, pixels[len(pixels) - 1][pixel])
                row.append(left_pixel)
            elif filr == 4:
                up_pixel = pixels[len(pixels) - 1][pixel]
                current = plus(pxl, paeth_predictor(left_pixel,
                               up_pixel, upleft_pixel))
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
if options.filout == "":
    print("Výstup není definován")
    exit(2)
if options.filinp == "":
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

x = ch.x
y = ch.y
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
fo = open(options.filout, "w")
fo.write(outstr)
fo.close()
