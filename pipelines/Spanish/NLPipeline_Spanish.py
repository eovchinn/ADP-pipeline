#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import re

METAPHOR_DIR = os.environ['METAPHOR_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
SPANISH_PIPELINE = "%s/pipelines/Spanish/run_spanish.sh" % METAPHOR_DIR
TMP_DIR = os.environ['TMP_DIR']

# paths
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR

def main():
	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", nargs="+", default=["-"] )
	parser.add_argument( "--outputdir", help="The output directory. Default is the dir of the input file.", default='' )
	parser.add_argument( "--parse", help="Parse tokenized text.", action="store_true", default=False )
	parser.add_argument( "--p2h", help="Process LF with Parser2Henry interface.", action="store_true", default=False )
	parser.add_argument( "--henry", help="Process LF with Henry.", action="store_false", default=True )
	parser.add_argument( "--kb", help="Path to knowledge base.", default='' )
	parser.add_argument( "--graph", help="ID of sentence to vizualize. Possible value -- allN, where N is the total number of outputs to vizualize.", default='1' )

	pa = parser.parse_args()
	outputdir = pa.outputdir

	for f in pa.input:
		fname = os.path.splitext(os.path.basename(f))[0]
		if len(pa.outputdir) == 0 : outputdir = os.path.dirname(f)

		# Spanish pipeline
		if pa.parse:
			spanish_proc = SPANISH_PIPELINE + ' < ' + f + ' | python ' + PARSER2HENRY + ' --output ' + os.path.join(outputdir,fname+'.obs')
			os.system(spanish_proc)	
		# Henry processing
		if pa.henry:
			henry = HENRY_DIR + "/bin/henry -m infer " + pa.kb + " " + os.path.join(outputdir,fname+".obs") + " -e " + HENRY_DIR + "/models/h93.py -T 120 -t 4 -O proofgraph,statistics > " + os.path.join(outputdir,fname+'.hyp')			
			os.system(henry)
		# Graphical vizualization
		if pa.graph != '0':
			matchObj = re.match(r'all(\d+)', pa.graph, re.M|re.I)
			if matchObj:
				for i in range(1, int(matchObj.group(1))+1):
					viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py --input ' + os.path.join(outputdir,fname+'.hyp') + ' --graph ' + str(i) + ' | dot -T pdf > ' + pa.outputdir + os.path.join(outputdir,fname+'_'+str(i)+'.pdf')
					os.system(viz)
			else:
				viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py --input ' + os.path.join(outputdir,fname+'.hyp') + ' --graph ' + pa.graph + ' | dot -T pdf > ' + pa.outputdir + os.path.join(outputdir,fname+'_'+pa.graph+'.pdf')
				os.system(viz)


if "__main__" == __name__: main()
