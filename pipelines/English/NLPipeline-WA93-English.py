#!/usr/bin/python

import argparse
import os
import re

# paths
boxerdir = '/home/ovchinnikova/candc/'
boxer2henry_path = '/home/ovchinnikova/isishare/coref_resolution/program/Boxer2Henry.pl'
henrydir = '/home/ovchinnikova/henry-n700/'

def main():

	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", nargs="+", default=["-"] )
	parser.add_argument( "--outputdir", help="The output directory. Default is the dir of the input file.", default='' )
	parser.add_argument( "--tok", help="Tokenize text.", action="store_true", default=False )
	parser.add_argument( "--parse", help="Parse tokenized text with C&C.", action="store_true", default=False )
	parser.add_argument( "--boxer", help="Process parsed text with Boxer.", action="store_true", default=False )
	parser.add_argument( "--b2h", help="Process LF with Boxer2Henry interface.", action="store_true", default=False )
	parser.add_argument( "--henry", help="Process LF with Henry.", action="store_false", default=True )
	parser.add_argument( "--kb", help="Path to knowledge base.", default='' )
	parser.add_argument( "--graph", help="Number of sentence to vizualize.", default='1' )
	
	pa = parser.parse_args()	

	outputdir = pa.outputdir
	for f in pa.input:
		fname = os.path.splitext(os.path.basename(f))[0]
		if len(pa.outputdir) == 0 : outputdir = os.path.dirname(f)

		# tokenization
		if pa.tok:
			tokenizer = boxerdir + 'bin/tokkie --input ' + f + ' --output ' + os.path.join(outputdir,fname+'.tok')
			os.system(tokenizer)	
		# parsing
		if pa.parse:
			candcParser = boxerdir + 'bin/candc --input ' + os.path.join(outputdir,fname+'.tok') + ' --output ' + pa.outputdir + os.path.join(outputdir,fname+'.ccg') +' --models ' + boxerdir + 'models/boxer --candc-printer boxer'
			os.system(candcParser)
		# Boxer processing
		if pa.boxer:
			boxer = boxerdir + 'bin/boxer --input ' + os.path.join(outputdir,fname+'.ccg') + ' --output ' + os.path.join(outputdir,fname+'.drs') + ' --semantics tacitus --resolve true'
			os.system(boxer) 
		# Boxer2Henry processing
		if pa.b2h:
			b2h = 'perl ' + boxer2henry_path + ' --input ' + os.path.join(outputdir,fname+'.drs') + ' --output ' + os.path.join(outputdir,fname+'.obs')
			os.system(b2h)
		# Henry processing
		if pa.henry:
			henry = henrydir + "bin/henry -m infer " + pa.kb + " " + os.path.join(outputdir,fname+".obs") + " -e " + henrydir + "models/h93.py -T 120 -t 4 -O proofgraph > " + os.path.join(outputdir,fname+'.hyp')			
			print henry
			os.system(henry)
		# Graphical vizualization
		if pa.graph != '0':
			matchObj = re.match(r'all(\d+)', pa.graph, re.M|re.I)
			if matchObj:
				for i in range(1, int(matchObj.group(1))+1):
					viz = 'python ' + henrydir + 'tools/proofgraph.py --input ' + os.path.join(outputdir,fname+'.hyp') + ' --graph ' + str(i) + ' | dot -T pdf > ' + pa.outputdir + os.path.join(outputdir,fname+'_'+str(i)+'.pdf')
					os.system(viz)
			else:
				viz = 'python ' + henrydir + 'tools/proofgraph.py --input ' + os.path.join(outputdir,fname+'.hyp') + ' --graph ' + pa.graph + ' | dot -T pdf > ' + pa.outputdir + os.path.join(outputdir,fname+'_'+pa.graph+'.pdf')
				os.system(viz)

if "__main__" == __name__: main()