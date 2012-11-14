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

def main():

	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", default=None )
	parser.add_argument( "--output", help="The output file", default=None )
	parser.add_argument( "--nonmerge", help="Add nonmerge constraints.", action="store_true", default=False )
	parser.add_argument( "--textid", help="Text ids added.", action="store_true", default=False )
	parser.add_argument( "--cost", help="Input observation cost.", type=int, default=1 )

	pa = parser.parse_args()	
	
	lines = open(pa.input, "r") if pa.input else sys.stdin
	ofile = open(pa.output, "w") if pa.output else sys.stdout
	
	#metafile = open(os.path.join(TMP_DIR,"meta"), "r")
	#meta = json.loads(metafile.readline())
	#metafile.close()

	output_str = ''
	id_prop_args_pattern = re.compile('(\[(\d+)\]:)?([^\[\(]+)(\((.+)\))?')
	sent_id_pattern = re.compile('id\((.+)\)')
	text_id_pattern = re.compile('% TEXTID\s*\(\s*([^\s\t]+)')
	sent_id = ''
	prop_id_counter = 0
	text_id = ''
	just_TEXT_ID = 0
	for line in lines:
		if line.startswith('%'): 
			TIDmatchObj = text_id_pattern.match(line)
			if TIDmatchObj:
				if text_id!='': ofile.write('))\n')
				text_id = TIDmatchObj.group(1)
				ofile.write('(O (name ' + text_id + ') (^')
				just_TEXT_ID = 1
				prop_id_counter = 0
		elif line.startswith('id('): 
			SIDmatchObj = sent_id_pattern.match(line)
			if SIDmatchObj:
				sent_id = SIDmatchObj.group(1)
				if not pa.textid: ofile.write('(O (name ' + sent_id + ') (^') 
			#else: print 'Strange sent id: ' + line
			
			if just_TEXT_ID == 1: just_TEXT_ID = 2
			else: just_TEXT_ID = 0
		elif line.strip() and just_TEXT_ID!=2:
			props = line.split(' & ')
			for prop in props:
				matchObj = id_prop_args_pattern.match(prop)
				if matchObj:
					prop_id_counter+= 1

					if matchObj.group(2): word_id = matchObj.group(2)
					else: word_id = 'ID'+str(prop_id_counter)

					prop_name = matchObj.group(3)
					prop_name.replace(' ','-')
					prop_name.replace('_','-')
					prop_name.replace(':','-')
					prop_name.replace('.','-')
					prop_name.replace('/','-')

					if matchObj.group(5): prop_args = matchObj.group(5)
					else: prop_args = ''
				
					nm = ''
					if prop_args!='': 
						prop_args = ' '+prop_args.replace(',',' ')
						if pa.nonmerge: 
							nm = ' (!='+prop_args+')'
							if matchObj.group(2): add_id2prop(matchObj.group(2),matchObj.group(5))

					ofile.write(' ('+prop_name+prop_args+' :'+str(pa.cost)+':'+sent_id+'-'+str(prop_id_counter)+':['+word_id+'])')
					if pa.nonmerge: ofile.write(nm)
				#else: print 'Strange proposition: ' + prop + '\n'				
			
			if pa.nonmerge: ofile.write(generate_sameID_nm())
			id2prop.clear()
			if not pa.textid: 
				ofile.write('))\n')
				prop_id_counter = 0

	if text_id!='': ofile.write('))\n')
	ofile.close()
					 
if "__main__" == __name__: main()