#!/usr/bin/python3
import sys

pnt=0
tapepnt=0
tape=[0]
brstack=[]
o=1

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

#istr=">++++++++[<+++++++++>-]<.>>+>+>++>[-]+<[>[->+<<++++>]<<]>.+++++++..+++.>"
#istr="+++[[-][+-]]+"
istr=">++++++++[<+++++++++>-]<.>>+>+>++>[-]+<[>[->+<<++++>]<<]>.+++++++..+++.>>+++++++.<<<[[-]<[-]>]<+++++++++++++++.>>.+++.------.--------.>>+.>++++.>>>>++++[>,.<-]"
#istr=".>+++++++.+++++++.-----."
#print(istr);

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
		#print(tape[tapepnt])
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
			#bude se skakat
			#print(' skočíme si')
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
			#nebude se skákat
			brstack.append(pnt)
			pnt+=1
	elif istr[pnt] == "]" :
		if tape[tapepnt] != 0:
			#bude se skakat zpatky
			pnt=brstack.pop();
			#print("pop " + str(pnt) + " ",end='')
		elif tape[tapepnt] == 0:
			#bude se pokracovat
			pnt=brstack.pop();
			#pnt+=1
	else:
		pnt+=1	
print();
#print(brstack);
#print(tape);
"""
	#debug
	print(tape,end='')
	print(" pnt ",end='')
	print(pnt,end='')
	print(" na ",end='')
	print(istr[pnt],end='')
	print(" na stacku ",end='')
	print(brstack)
	#+++++++++++++++++++++
"""
