#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import re
import os
import json
from collections import defaultdict

# global vars
id2prop = defaultdict(list)

TMP_DIR = os.environ['TMP_DIR']

def add_id2prop(id_str,arg_str):
	ids = id_str.split(',')
	args = arg_str.split(',')
	for id in ids:
		id2prop[id].append(args[0])	

def generate_sameID_nm():
	nm = ''
	for id in id2prop.keys():
		if len(id2prop[id])>1:
			nm += ' (!='
			for arg in id2prop[id]:
				nm += ' ' + arg 
			nm += ')'
	return nm	

def check_prep(pred):
	prepositions = [
	"abaft",
	"aboard",
	"about",
	"above",
	"absent",
	"across",
	"afore",
	"after",
	"against",
	"along",
	"alongside",
	"amid",
	"amidst",
	"among",
	"amongst",
	"around",
	"as",
	"aside",
	"astride",
	"at",
	"athwart",
	"atop",
	"barring",
	"before",
	"behind",
	"below",
	"beneath",
	"beside",
	"besides",
	"between",
	"betwixt",
	"beyond",
	"but",
	"by",
	"concerning",
	"despite",
	"during",
	"except",
	"excluding",
	"failing",
	"following",
	"for",
	"from",
	"given",
	"in",
	"including",
	"inside",
	"into",
	"lest",
	"like",
	"minus",
	"modulo",
	"near",
	"next",
	"of",
	"off",
	"on",
	"onto",
	"opposite",
	"out",
	"outside",
	"over",
	"pace",
	"past",
	"plus",
	"pro",
	"qua",
	"regarding",
	"round",
	"sans",
	"save",
	"since",
	"than",
	"through",
	"throughout",
	"till",
	"times",
	"to",
	"toward",
	"towards",
	"under",
	"underneath",
	"unlike",
	"until",
	"up",
	"upon",
	"versus",
	"via",
	"vice",
	"with",
	"within",
	"without",
	"worth"]

	for p in prepositions:
		if p == pred: return pred+'-in'
	return pred

def main():

	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", default=None )
	parser.add_argument( "--output", help="The output file", default=None )
	parser.add_argument( "--nonmerge", help="Add nonmerge constraints.", action="store_true", default=False )
	parser.add_argument( "--cost", help="Input observation cost.", type=int, default=1 )

	pa = parser.parse_args()	
	
	lines = open(pa.input, "r") if pa.input else sys.stdin
	ofile = open(pa.output, "w") if pa.output else sys.stdout	

	output_str = ''
	id_prop_args_pattern = re.compile('\[([^\]]*)\]:([^\[\(]+)(\((.+)\))?')
	prop_name_pattern = re.compile('(.+)-([nvarp])$')
	sent_id_pattern = re.compile('id\((.+),.+\)')
	sent_id = ''
	prop_id_counter = 0
	text_id = ''
	for line in lines:
		if line.startswith('%'): continue
		elif line.startswith('id('): 
			SIDmatchObj = sent_id_pattern.match(line)
			if SIDmatchObj:
				sent_id = SIDmatchObj.group(1)
				ofile.write('(O (name ' + sent_id + ') (^') 
			#else: print 'Strange sent id: ' + line

		elif line[0].isdigit(): continue
		elif line.strip():
			props = line.split(' & ')
			for prop in props:
				matchObj = id_prop_args_pattern.match(prop)
				if matchObj:
					prop_id_counter+= 1

					if matchObj.group(1): word_id = matchObj.group(1)
					else: word_id = 'ID'+str(prop_id_counter)

					prop_name = matchObj.group(2)
					prop_name.replace(' ','-')
					prop_name.replace('_','-')
					prop_name.replace(':','-')
					prop_name.replace('.','-')
					prop_name.replace('/','-')
					propMatchObj = prop_name_pattern.match(prop_name)
					if propMatchObj:
						pname = propMatchObj.group(1)
						postfix = propMatchObj.group(2)
						if postfix == 'n' : postfix = 'nn'
						elif postfix == 'v' : postfix = 'vb'
						elif postfix == 'a' : postfix = 'adj'
						elif postfix == 'p' : postfix = 'in'
						elif postfix == 'r' : postfix = 'rb'
						prop_name = pname+'-'+postfix
					else:
						prop_name = check_prep(prop_name)
	
					nm = ''
					if matchObj.group(4): 
						prop_args = matchObj.group(4)
						prop_args = ' '+prop_args.replace(',',' ')
						if pa.nonmerge: 
							nm = ' (!='+prop_args+')'
							if matchObj.group(1): add_id2prop(matchObj.group(1),matchObj.group(4))
					else: prop_args = ''
	
					ofile.write(' ('+prop_name+prop_args+' :'+str(pa.cost)+':'+sent_id+'-'+str(prop_id_counter)+':['+word_id+'])')
					if pa.nonmerge: ofile.write(nm)
				#else: print 'Strange proposition: ' + prop + '\n'				
			
			if pa.nonmerge: ofile.write(generate_sameID_nm())
			ofile.write('))\n')
			prop_id_counter = 0
			id2prop.clear()

	ofile.close()
					 
if "__main__" == __name__: main()