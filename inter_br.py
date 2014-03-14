#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
#neco
pnt=0
tapepnt=0
tape=[0]
brstack=[]
o=1
istr=""

#Parsovani a nacitani
parser = OptionParser(usage="usage: %prog [options] files", version="%prog 0.1")
parser.add_option("-f","--FileName", action="store", dest="filename", type="string", help="Nastaveni jmena vstupniho souboru")

args = sys.argv[1:]
(options, args) = parser.parse_args()
if options.filename:
	if os.path.exists(options.filename):
		with open(options.filename, mode='r', encoding='utf-8') as stream:
			for intp in stream.readlines():
				istr=istr+intp
	else:
		print("Soubor neexistuje")
else:
	istr = input()


#Definice pro getchary a putchary
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
    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys
    def __call__(self):
        import sys, tty, termios
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

#parser
while pnt < len(istr):
	if istr[pnt] == "+" :
		tape[tapepnt]+=1
		pnt+=1
	elif istr[pnt] == "-" :
		tape[tapepnt]-=1
		pnt+=1
	elif istr[pnt] == "." :
		putchar(tape[tapepnt])
		pnt+=1
	elif istr[pnt] == "," :
		tape[tapepnt]=ord(getch())
		pnt+=1
	elif istr[pnt] == ">" :
		if len(tape) - 1 == tapepnt:
			tape=tape+[0]
		tapepnt+=1
		pnt+=1
	elif istr[pnt] == "<" :
		tapepnt-=1
		pnt+=1
	elif istr[pnt] == "[" :
		if tape[tapepnt] == 0:
			pnt+=1;
			while o > 0 :
				if istr[pnt] == "[":
					o+=1
					pnt+=1
				elif istr[pnt] == "]":
					o-=1
					pnt+=1
				else:
					pnt+=1
			o=1
		elif tape[tapepnt] != 0:
			brstack.append(pnt)
			pnt+=1
	elif istr[pnt] == "]" :
		if tape[tapepnt] != 0:
			pnt=brstack.pop()
		elif tape[tapepnt] == 0:
			pnt=brstack.pop()
	else:
		pnt+=1	
print();
