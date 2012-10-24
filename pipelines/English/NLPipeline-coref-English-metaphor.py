#!/usr/bin/python

import argparse
import os
import re

# paths
boxerdir = '/home/ovchinnikova/candc/'
boxer2henry_path = './Boxer2Henry.pl'
henrydir = '/home/ovchinnikova/henry-n700/'
features = '../../models/data'
kbpath = '../../models/data/kb-wnfn-noder-lmap.da'

def extract_hypotheses(filepath,outputdir,fname):
	lines = open(filepath, "r")
	fout = open(os.path.join(outputdir,fname+".out"), 'w')

	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''

	for line in lines:
		matchObj = p.match(line)
		if matchObj: target = matchObj.group(1)	
		elif line.startswith('<hypothesis'): hypothesis_found = True
		else:
			if hypothesis_found:	
				fout.write(target+': '+line)
				hypothesis_found = False
	fout.close()

def main():
	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", nargs="+", default=["-"] )
	parser.add_argument( "--outputdir", help="The output directory. Default is the dir of the input file.", default='' )
	parser.add_argument( "--kb", help="Path to knowledge base.", default='' )
	parser.add_argument( "--kbcompiled", help="Use compiled WN-FN knowledge base.", action="store_true", default=False )
	
	pa = parser.parse_args()	

	outputdir = pa.outputdir
	for f in pa.input:
		fname = os.path.splitext(os.path.basename(f))[0]
		if len(pa.outputdir) == 0 : outputdir = os.path.dirname(f)

		# tokenization
		tokenizer = boxerdir + 'bin/tokkie --input ' + f + ' --output ' + os.path.join(outputdir,fname+'.tok')
		os.system(tokenizer)	

		# parsing
		candcParser = boxerdir + 'bin/candc --input ' + os.path.join(outputdir,fname+'.tok') + ' --output ' + pa.outputdir + os.path.join(outputdir,fname+'.ccg') +' --models ' + boxerdir + 'models/boxer --candc-printer boxer'
		os.system(candcParser)

		# Boxer processing
		boxer = boxerdir + 'bin/boxer --input ' + os.path.join(outputdir,fname+'.ccg') + ' --output ' + os.path.join(outputdir,fname+'.drs') + ' --semantics tacitus --resolve true'
		os.system(boxer) 

		# Boxer2Henry processing
		b2h = 'perl ' + boxer2henry_path + ' --input ' + os.path.join(outputdir,fname+'.drs') + ' --output ' + os.path.join(outputdir,fname+'.obs')
		os.system(b2h)

		# Henry processing
		if pa.kbcompiled:
			henry = henrydir + "bin/henry -m infer " + henrydir + "models/w.hard " + pa.kb + " " + os.path.join(outputdir,fname+".obs") + " -d 3 -T 120 -e " + henrydir + "models/i12.py -O statistics -f '--datadir " + features + "' -b " + kbpath + " -t 4 > " + os.path.join(outputdir,fname+'.hyp')
			os.system(henry)
		else:
			henry = henrydir + "bin/henry -m infer " + henrydir + "models/w.hard " + pa.kb + " " + os.path.join(outputdir,fname+".obs") + " -d 3 -T 120 -e " + henrydir + "models/i12.py -O statistics -f '--datadir " + features + "' -t 4 > " + os.path.join(outputdir,fname+'.hyp')
			os.system(henry)

	extract_hypotheses(os.path.join(outputdir,fname+".hyp"),outputdir,fname)

if "__main__" == __name__: main()