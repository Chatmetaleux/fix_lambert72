import os
import sys
import datetime

path_parse = "xyGridLb72.dat"
path_out = "L72.txt"

nf = open(path_out, 'w')
dico=[]

p=""
t=""

with open(path_parse) as f_pos:
	for line in f_pos:
		s=line.replace("     ","\t").replace("\n","")
		s=s.replace("    ","\t")
		s=s.replace("   ","\t")
		s=s.replace("  ","\t")
		s=s.replace(" ","\t")
		
		ss=s.split("\t")
		if t=="":
			print ss
		c=ss[2]
		
		if c!=p:
			if t!="":
				t="[ "+t+" ],\n"
				nf.write(t)
			p=c
			t=""
		
		if t=="":
			t= "[%s , %s]" % (ss[3],ss[4])
		else:
			t+= ", [%s , %s]" % (ss[3],ss[4])
	
	if t!="":
		t="[ "+t+" ],"
		nf.write(t)
		
	nf.close()