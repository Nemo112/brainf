#!/usr/bin/python3
pnt=0
tapepnt=0
tape=[0]
brstack=[]
o=1
def putchar(n):
	print(chr(n), end='')
#istr=">++++++++[<+++++++++>-]<.>>+>+>++>[-]+<[>[->+<<++++>]<<]>.+++++++..+++.>"
#istr="+++[[-][+-]]+"
istr=">++++++++[<+++++++++>-]<.>>+>+>++>[-]+<[>[->+<<++++>]<<]>.+++++++..+++.>>+++++++.<<<[[-]<[-]>]<+++++++++++++++.>>.+++.------.--------.>>+.>++++."
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
