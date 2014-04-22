#!/usr/bin/python2
from sys import*
def f(u,c,k):
 while(c[-2]>=k)*u:
  j,u='[]><+-,.'.find(u[0]),u[1:]
  b=(j>=0)*(1-j%2*2);c[-2]+=b*(j<2)
  while b*c[c[-1]]and j<1:f(u,c,k+1);c[-2]+=1
  b*=c[-2]==k;c[[-1,c[-1],-3][j/2-1]]+=b
  if(j==6)*b:c[c[-1]]=ord(stdin.read(1))
  if(j>6)*b:stdout.write(chr(c[c[-1]]))
f(open(argv[1]).read(),[0]*30003,0)
