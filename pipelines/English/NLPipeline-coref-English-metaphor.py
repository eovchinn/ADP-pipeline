#!/usr/bin/python

import argparse
import os
import re
import sys

METAPHOR_DIR = os.environ['METAPHOR_DIR']
BOXER_DIR = os.environ['BOXER_DIR']
HENRY_DIR = os.environ['HENRY_DIR']

# paths
boxer2henry_path = "%s/pipelines/English/Boxer2Henry.pl" % METAPHOR_DIR
features = "%s/models/English-features-henry" % METAPHOR_DIR
kbpath = "%s/KBs/English/kb-wnfn-noder-lmap.da" % METAPHOR_DIR
extract_hypotheses_path = "%s/pipelines/common/extract_hypotheses.py" % METAPHOR_DIR

def main():
	parser = argparse.ArgumentParser( description="English discource processing pipeline with coref for metaphor project." )
	parser.add_argument( "--outputdir", help="The output directory. Default is METAPHOR_DIR.", default=METAPHOR_DIR )
	parser.add_argument( "--kb", help="Path to knowledge base.", default='' )
	parser.add_argument( "--kbcompiled", help="Use compiled WN-FN knowledge base.", action="store_true", default=False )

	pa = parser.parse_args()
	if len(pa.outputdir) != 0: outputdir = pa.outputdir
	input = sys.stdin.read()

       # tokenization
	tokenizer = 'echo "' + input + '"' + ' | ' + BOXER_DIR + '/bin/tokkie --stdin'

	# parsing
	candcParser = BOXER_DIR + '/bin/candc --output ' + os.path.join(outputdir,"tmp.ccg") + ' --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
	

	# Boxer processing
	boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --input ' + os.path.join(outputdir,"tmp.ccg")

	# Boxer2Henry processing
	b2h = 'perl ' + boxer2henry_path + ' --output ' + os.path.join(outputdir,"tmp.obs") + ' --nonmerge sameargs'

	boxer_proc = tokenizer + ' | ' + candcParser + ' | ' + boxer + ' | ' + b2h
	os.system(boxer_proc)
	
	# Henry processing
	if pa.kbcompiled:
		henry = HENRY_DIR + "/bin/henry -m infer " + HENRY_DIR + "/models/w.hard " + pa.kb + " " + os.path.join(outputdir,"tmp.obs") + " -d 3 -T 120 -e " + HENRY_DIR + "/models/i12.py -O proofgraph,statistics -f '--datadir " + features + "' -b " + kbpath + " -t 4"
	else:
		henry = HENRY_DIR + "/bin/henry -m infer " + HENRY_DIR + "/models/w.hard " + pa.kb + " " + os.path.join(outputdir,"tmp.obs") + " -d 3 -T 120 -e " + HENRY_DIR + "/models/i12.py -O proofgraph,statistics -f '--datadir " + features + "' -t 4"

	# henry inference and extraction of hypotheses
	henry_hyp_extr = henry + ' | python ' + extract_hypotheses_path
	os.system(henry_hyp_extr)

if "__main__" == __name__: main()