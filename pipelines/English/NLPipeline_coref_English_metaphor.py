#!/usr/bin/python

import os
import re
import sys
import json
import time
from subprocess import Popen, PIPE, STDOUT

METAPHOR_DIR = os.environ['METAPHOR_DIR']
BOXER_DIR = os.environ['BOXER_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
TMP_DIR = os.environ['TMP_DIR']

# paths
boxer2henry_path = "%s/pipelines/English/Boxer2Henry.pl" % METAPHOR_DIR
#features = "%s/models/English-features-henry" % METAPHOR_DIR
kbpath = "%s/KBs/English/kb-wnfn-noder-lmap.da" % METAPHOR_DIR
extract_hypotheses_path = "%s/pipelines/common/extract_hypotheses.py" % METAPHOR_DIR
kb = ''

# switches
kbcompiled = False

def extract_hypotheses(inputString):
	output_struct = []
	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''
	hypothesis = ''
	unification = False
	explanation = False

	for line in inputString.splitlines():
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
			output_struct_item['description'] = 'Abductive engine output; abductive_hypothesis: metaphor interpretation; abductive_unification: unifications happened or not; abductive_explanation: axioms applied or not'
			output_struct.append(output_struct_item) 
			target = ''
			unification = False
			explanation = False

	return json.dumps(output_struct)
	
def generate_Boxer_input(input_dict):
	output_str = ''
	for id in input_dict.keys():
		output_str += "<META>'" + id + "'\n\n " + input_dict[id] + "\n\n" 
	return output_str	

def English_ADP(input_dict):
	start_time = time.time()	

	input_str = generate_Boxer_input(input_dict)      

       # tokenization
	tokenizer = 'echo "' + input_str + '"' + ' | ' + BOXER_DIR + '/bin/tokkie --stdin'

	# parsing
	candcParser = BOXER_DIR + '/bin/candc --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'	

	# Boxer processing
	boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --stdin'

	# Boxer2Henry processing
	b2h = 'perl ' + boxer2henry_path + ' --nonmerge sameargs'

	boxer_proc = tokenizer + ' | ' + candcParser + ' | ' + boxer + ' | ' + b2h
	#os.system(boxer_proc)

	boxer_time = 10 							# Assumed Boxer time in seconds
	time_all_henry = 600 - boxer_time		    			# all time rest for Henry in seconds	
	time_unit_henry = str(int(time_all_henry/len(input_dict)))	# time for one interpretation in Henry in seconds
	
	# Henry processing
	if kbcompiled:
		henry = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry + ' -b ' + kbpath 
	else:
		henry = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry

	all_proc = boxer_proc + ' | ' + henry
	#os.system(all_proc)

	pipeline = Popen(all_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	henry_output = pipeline.stdout.read()

	return extract_hypotheses(henry_output)

if "__main__" == __name__: main()