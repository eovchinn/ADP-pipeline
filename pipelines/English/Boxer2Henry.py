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
pred2farg = defaultdict(list)

TMP_DIR = os.environ['TMP_DIR']

def add_id2prop(id_str,arg):
	ids = id_str.split(',')
	for id in ids:
		id2prop[id].append(arg)	

def generate_sameID_nm():
	nm = ''
	for id in id2prop.keys():
		if len(id2prop[id])>1:
			nm += ' (!='
			for arg in id2prop[id]:
				nm += ' ' + arg 
			nm += ')'
	return nm	

def generate_freqPred_nm():
	nm = ''
	for pred in pred2farg.keys():
		if len(pred2farg[pred])>1:
			nm += ' (!='
			for arg in pred2farg[pred]:
				nm += ' ' + arg 
			nm += ')'
	return nm

prepositions = {
	"abaft": 1,
	"aboard": 1,
	"about": 1,
	"above": 1,
	"absent": 1,
	"across": 1,
	"afore": 1,
	"after": 1,
	"against": 1,
	"along": 1,
	"alongside": 1,
	"amid": 1,
	"amidst": 1,
	"among": 1,
	"amongst": 1,
	"around": 1,
	"as": 1,
	"aside": 1,
	"astride": 1,
	"at": 1,
	"athwart": 1,
	"atop": 1,
	"barring": 1,
	"before": 1,
	"behind": 1,
	"below": 1,
	"beneath": 1,
	"beside": 1,
	"besides": 1,
	"between": 1,
	"betwixt": 1,
	"beyond": 1,
	"but": 1,
	"by": 1,
	"concerning": 1,
	"despite": 1,
	"during": 1,
	"except": 1,
	"excluding": 1,
	"failing": 1,
	"following": 1,
	"for": 1,
	"from": 1,
	"given": 1,
	"in": 1,
	"including": 1,
	"inside": 1,
	"into": 1,
	"lest": 1,
	"like": 1,
	"minus": 1,
	"modulo": 1,
	"near": 1,
	"next": 1,
	"of": 1,
	"off": 1,
	"on": 1,
	"onto": 1,
	"opposite": 1,
	"out": 1,
	"outside": 1,
	"over": 1,
	"pace": 1,
	"past": 1,
	"plus": 1,
	"pro": 1,
	"qua": 1,
	"regarding": 1,
	"round": 1,
	"sans": 1,
	"save": 1,
	"since": 1,
	"than": 1,
	"through": 1,
	"throughout": 1,
	"till": 1,
	"times": 1,
	"to": 1,
	"toward": 1,
	"towards": 1,
	"under": 1,
	"underneath": 1,
	"unlike": 1,
	"until": 1,
	"up": 1,
	"upon": 1,
	"versus": 1,
	"via": 1,
	"vice": 1,
	"with": 1,
	"within": 1,
	"without": 1,
	"worth": 1}

def check_prep(pred):
	if pred in prepositions: 
		return pred+'-in'
	return pred

def main():

	parser = argparse.ArgumentParser( description="Boxer2Henry converter." )
	parser.add_argument( "--input", help="Input file", default=None )
	parser.add_argument( "--output", help="Output file", default=None )
	parser.add_argument( "--nonmerge", help="Add nonmerge constraints. Values: samepred (args of a pred cannot be merged), sameid (args of preds with same id cannot be merged), freqpred (args of frequent preds cannot be merged)", nargs='+', default=[] )
	parser.add_argument( "--cost", help="Input observation costs.", type=int, default=1 )

	pa = parser.parse_args()	

	if 'samepred' in pa.nonmerge:  samepred = True
	else: samepred = False
	if 'sameid' in pa.nonmerge: sameid = True
	else: sameid = False
	if 'freqpred' in pa.nonmerge: freqpred = True
	else: freqpred = False
	
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
					
					pred4nm = None
					if propMatchObj:
						pname = propMatchObj.group(1)
						postfix = propMatchObj.group(2)
						if postfix == 'n' : postfix = 'nn'
						elif postfix == 'v' : postfix = 'vb'
						elif postfix == 'a' : postfix = 'adj'
						elif postfix == 'p' : 
							postfix = 'in'
							pred4nm = pname+'-'+postfix
						elif postfix == 'r' : postfix = 'rb'
						prop_name = pname+'-'+postfix
					else:
						prop_name = check_prep(prop_name)
						pred4nm = prop_name
	
					nm = ''
					if matchObj.group(4): 
						prop_args = matchObj.group(4)
						prop_args = ' '+prop_args.replace(',',' ')
						if samepred: nm = ' (!='+prop_args+')'
						if sameid or freqpred: 
							args = prop_args.split()
							if sameid and matchObj.group(1): add_id2prop(matchObj.group(1),args[0])
							if freqpred and pred4nm:
								if args[0] not in pred2farg[pred4nm]: 
									pred2farg[pred4nm].append(args[0])
					else: prop_args = ''
	
					ofile.write(' ('+prop_name+prop_args+' :'+str(pa.cost)+':'+sent_id+'-'+str(prop_id_counter)+':['+word_id+'])')
					if samepred: ofile.write(nm)
				#else: print 'Strange proposition: ' + prop + '\n'				
			
			if sameid: ofile.write(generate_sameID_nm())
			if freqpred: ofile.write(generate_freqPred_nm())
			ofile.write('))\n')
			prop_id_counter = 0
			id2prop.clear()
			pred2farg.clear()

	ofile.close()
					 
if "__main__" == __name__: main()
