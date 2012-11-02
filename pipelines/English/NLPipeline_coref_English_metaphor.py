#!/usr/bin/python

import os
import re
import sys
import json
from collections import defaultdict

METAPHOR_DIR = os.environ['METAPHOR_DIR']
BOXER_DIR = os.environ['BOXER_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
TMP_DIR = os.environ['TMP_DIR']

# paths
boxer2henry_path = "%s/pipelines/English/Boxer2Henry.pl" % METAPHOR_DIR
features = "%s/models/English-features-henry" % METAPHOR_DIR
kbpath = "%s/KBs/English/kb-wnfn-noder-lmap.da" % METAPHOR_DIR
extract_hypotheses_path = "%s/pipelines/common/extract_hypotheses.py" % METAPHOR_DIR

# switches
kbcompiled = False
kb = ''

def extract_hypotheses(filename):
	f = open(filename, 'r')
	#output_struct = defaultdict(dict)	
	output_struct = []
	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''
	hypothesis = ''
	unification = False
	explanation = False

	for line in f:
		output_struct_item={} 
		matchObj = p.match(line)
		if matchObj: target = matchObj.group(1)	
		elif line.startswith('<hypothesis'): hypothesis_found = True
		elif line.startswith('</hypothesis>'): hypothesis_found = False 
		elif hypothesis_found: hypothesis = line
		elif line.startswith('<unification'): unification = True
		elif line.startswith('<explanation'): explanation = True
		elif line.startswith('</result-inference>'):
			output_struct_item['annotation_id'] = target
			output_struct_item['abductive_hypothesis'] = hypothesis
			output_struct_item['abductive_unification'] = unification
			output_struct_item['abductive_explanation'] = explanation
			output_struct.append(output_struct_item) 
			target = ''
			unification = False
			explanation = False

	return json.dumps(output_struct)
	

def English_ADP(input):

       # tokenization
	tokenizer = 'echo "' + input + '"' + ' | ' + BOXER_DIR + '/bin/tokkie --stdin'

	# parsing
	candcParser = BOXER_DIR + '/bin/candc --output ' + os.path.join(TMP_DIR,"tmp.ccg") + ' --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
	

	# Boxer processing
	boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --input ' + os.path.join(TMP_DIR,"tmp.ccg")

	# Boxer2Henry processing
	b2h = 'perl ' + boxer2henry_path + ' --output ' + os.path.join(TMP_DIR,"tmp.obs") + ' --nonmerge sameargs'

	boxer_proc = tokenizer + ' | ' + candcParser + ' | ' + boxer + ' | ' + b2h
	os.system(boxer_proc)
	
	# Henry processing
	if kbcompiled:
		henry = HENRY_DIR + "/bin/henry -m infer " + HENRY_DIR + "/models/w.hard " + kb + " " + os.path.join(TMP_DIR,"tmp.obs") + " -d 3 -T 120 -e " + HENRY_DIR + "/models/i12.py -O proofgraph,statistics -f '--datadir " + features + "' -b " + kbpath + " -t 4 > " + os.path.join(TMP_DIR,"tmp.hyp")
	else:
		henry = HENRY_DIR + "/bin/henry -m infer " + HENRY_DIR + "/models/w.hard " + kb + " " + os.path.join(TMP_DIR,"tmp.obs") + " -d 3 -T 120 -e " + HENRY_DIR + "/models/i12.py -O proofgraph,statistics -f '--datadir " + features + "' -t 4 > " + os.path.join(TMP_DIR,"tmp.hyp")

	# henry inference 
	os.system(henry)

	return extract_hypotheses(os.path.join(TMP_DIR,"tmp.hyp"))

if "__main__" == __name__: main()