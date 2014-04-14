import sys;V=sys.argv;n=int(V[2]);r=V[1];S=len;R=range;C=R(32,127)
Z=[];z=-1;D='d(r,p,';F='for j in ';O=lambda c:ord(c[z])	 
def f(i,a):
 if i>=S(r):return a,i
 c=r[i];x=0;I="|)]".find(c)
 if c in"([|":x,i=f(i+1,Z)
# print i,a,c,I,x
 if I+1:return(['|',a,x],[a],['[',a])[I],i
 if'\\'==c:i+=1;x=c+r[i]
 return f(i+1,a+[x or c])
def d(r,a,s):
# print r,a,s
 if S(s)>n:return
 while a==Z:
	if r==Z:print s;return
	a=r[z];r=r[:z]
#       a=r.pop(z)
 e=a[z];p=a[0:z]
 if'|'==a[0]:d(r,a[1],s);d(r,a[2],s)
 elif'['==a[0]:
	g=a[1];N=g[0]=='^';B=[0]*127
	if N:g=g[1:]
	for i in R(0,S(g)):
	 if'-'==g[i]:exec F+'R(O(g[i-1]),O(g[i+1])):B[j]=1'
	 else:B[O(g[i])]=1
	for c in C:N^B[c]<1or d(r,Z,chr(c)+s)
 elif' '>e:d(r+[p],e,s)
 else:c=p[:z];exec{'.':F+'C:'+D+'s+chr(j))','?':D+'s);d(r,p[:z],s)','*':F+'R(0,n+1):d(r,c,s);c+=[p[z]]','+':"d(r,p+['*',p[z]],s)"}.get(e,D+'e[z]+s)')
d(Z,f(0,Z)[0],"")
