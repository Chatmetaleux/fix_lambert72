import os
import sys
import datetime

path_parse = "hBG03.dat"
path_out = "Z.txt"

nf = open(path_out, 'w')
dico=[]

p=""
t=""

with open(path_parse) as f_pos:
	for line in f_pos:
		s=line.replace("  ","\t").replace("\n","")
		s=s.replace(" ","\t")
		
		ss=s.split("\t")
		if t=="":
			print ss
		c=ss[0]
		
		if c!=p:
			if t!="":
				t="[ "+t+" ],\n"
				nf.write(t)
			p=c
			t=""
		
		if t=="":
			t= " %s" % ss[2]
		else:
			t+= ", %s" % ss[2]
	
	if t!="":
		t="[ "+t+" ],"
		nf.write(t)
		
	nf.close()