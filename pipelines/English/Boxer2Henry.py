#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Ekaterina Ovchinnikova <katya@isi.edu> (2012)

# English LF converter processing Boxer output and returning Henry input logical forms with nonmerge constraints.

# In order to see options, run
# $ python Boxer2Henry.py -h

import argparse
import sys
import re
import os
import json
from collections import defaultdict

# global vars
id2prop = defaultdict(list)
pred2farg = defaultdict(list)

# Add word ids mapped to first args of corresponding propositions
def add_id2prop(id_str,arg):
	ids = id_str.split(',')
	for id in ids:
		id2prop[id].append(arg)	

# Generate nonmerge constraints, so that 
# propositions with the same word ids could not be unified
def generate_sameID_nm():
	nm = ''
	for id in id2prop.keys():
		if len(id2prop[id])>1:
			nm += ' (!='
			for arg in id2prop[id]:
				nm += ' ' + arg 
			nm += ')'
	return nm	

# Generate nonmerge constraints, so that 
# frequent predicates could not be unified
def generate_freqPred_nm():
	nm = ''
	for pred in pred2farg.keys():
		if len(pred2farg[pred])>1:
			nm += ' (!='
			for arg in pred2farg[pred]:
				nm += ' ' + arg 
			nm += ')'
	return nm

# English preposition list 
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

# Check if a predicate is a preposition
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

	# Set nonmerge options
	if 'samepred' in pa.nonmerge:  samepred = True
	else: samepred = False
	if 'sameid' in pa.nonmerge: sameid = True
	else: sameid = False
	if 'freqpred' in pa.nonmerge: freqpred = True
	else: freqpred = False
	
	# Read input
	lines = open(pa.input, "r") if pa.input else sys.stdin

	# Set output file
	ofile = open(pa.output, "w") if pa.output else sys.stdout	

	output_str = ''
	sent_id = ''
	prop_id_counter = 0

	# Pattern for parsing: [word id list]:pred_name(args)
	id_prop_args_pattern = re.compile('\[([^\]]*)\]:([^\[\(]+)(\((.+)\))?')
	# Pattern for parsing: pred_name_base-postfix
	prop_name_pattern = re.compile('(.+)-([nvarp])$')
	# Pattern for parsing: id(sentence_id,..) 
	sent_id_pattern = re.compile('id\((.+),.+\)')

	for line in lines:
		# Ignore commented strings		
		if line.startswith('%'): continue
		# Define sentence id
		elif line.startswith('id('): 
			SIDmatchObj = sent_id_pattern.match(line)
			if SIDmatchObj:
				sent_id = SIDmatchObj.group(1)
				ofile.write('(O (name ' + sent_id + ') (^') 
			#else: print 'Strange sent id: ' + line
		# Ignore lemmatized word list
		elif line[0].isdigit(): continue
		# Parse propositions
		elif line.strip():
			props = line.split(' & ')
			for prop in props:
				matchObj = id_prop_args_pattern.match(prop)
				if matchObj:
					prop_id_counter+= 1

					# Define word id string
					if matchObj.group(1): word_id_str = matchObj.group(1)
					else: word_id_str = 'ID'+str(prop_id_counter)

					# Normalize predicate name
					prop_name = matchObj.group(2)
					prop_name.replace(' ','-')
					prop_name.replace('_','-')
					prop_name.replace(':','-')
					prop_name.replace('.','-')
					prop_name.replace('/','-')
					propMatchObj = prop_name_pattern.match(prop_name)
					
					# Set predicate name to which nonmerge constraints are applied
					pred4nm = None
					# Predicate name contains postfix					
					if propMatchObj:
						pname = propMatchObj.group(1)
						postfix = propMatchObj.group(2)
						# Normalize postfixes
						if postfix == 'n' : postfix = 'nn' 	# Noun
						elif postfix == 'v' : postfix = 'vb'	# Verb
						elif postfix == 'a' : postfix = 'adj'	# Adjective
						elif postfix == 'p' : 			# Preposition
							postfix = 'in'
							# It can be a subject 
							# to nonmerge constraints							
							pred4nm = pname+'-'+postfix
						elif postfix == 'r' : postfix = 'rb'	# Adverb
						prop_name = pname+'-'+postfix
					else:
						# Boxer sometimes does not mark prepositions.
						# Fixing it.
						prop_name = check_prep(prop_name)
						# It can be a subject 
						# to nonmerge constraints
						pred4nm = prop_name
	
					# Set nonmerge constraints
					nm = ''
					# Proposition has arguments
					if matchObj.group(4): 
						prop_args = matchObj.group(4)
						prop_args = ' '+prop_args.replace(',',' ')
						# Arguments of the same predicate cannot be unified
						if samepred: nm = ' (!='+prop_args+')'
						if sameid or freqpred: 
							args = prop_args.split()
							# Add first arg of this proposition to dict id2prop
							if sameid and matchObj.group(1): add_id2prop(word_id_str,args[0])
							# Frequent predicates cannot be unified
							if freqpred and pred4nm:
								if args[0] not in pred2farg[pred4nm]: 
									pred2farg[pred4nm].append(args[0])
					# Proposition has no arguments					
					else: prop_args = ''
					
					# Write Henry representation of the proposition into output
					ofile.write(' ('+prop_name+prop_args+' :'+str(pa.cost)+':'+sent_id+'-'+str(prop_id_counter)+':['+word_id_str+'])')
					# Write nonmerge constraints for 'samepred' into output
					if samepred: ofile.write(nm)
				#else: print 'Strange proposition: ' + prop + '\n'				
			
			# Write nonmerge constraints for 'sameid' into output
			if sameid: ofile.write(generate_sameID_nm())
			# Write nonmerge constraints for 'freqpred' into output
			if freqpred: ofile.write(generate_freqPred_nm())

			ofile.write('))\n')

			prop_id_counter = 0
			id2prop.clear()
			pred2farg.clear()

	ofile.close()
					 
if "__main__" == __name__: main()
