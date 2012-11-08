#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
from subprocess import Popen, PIPE, STDOUT

METAPHOR_DIR = os.environ['METAPHOR_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
FARSI_PIPELINE = "%s/pipelines/Farsi/LF_Pipeline" % METAPHOR_DIR
TMP_DIR = os.environ['TMP_DIR']

# paths
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR
kbpath = ''
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

	return json.dumps(output_struct,ensure_ascii=False)

def generate_text_input(input_dict):
	output_str = ''
	for id in input_dict.keys():
		output_str += '.TEXTID('+id+').\n\n'+input_dict[id].replace("\u2019", "'") + "\n\n" 
	return output_str	

def Farsi_ADP(input_dict):
	start_time = time.time()
	input_str = generate_text_input(input_dict)

       # Run Farsi pipeline
	parser_proc = FARSI_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge --textid'

	parser_pipeline = Popen(parser_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	parser_output = parser_pipeline.communicate(input=input_str)[0]

	parser_time = (time.time()-start_time)*0.001			# Parser processing time in seconds
	time_all_henry = 600 - parser_time		    			# all time rest for Henry in seconds	
	time_unit_henry = str(int(time_all_henry/len(input_dict)))	# time for one interpretation in Henry in seconds

	# Henry processing
	if kbcompiled:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry + ' -b ' + kbpath 
	else:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry 

	henry_pipeline = Popen(henry_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	henry_output = henry_pipeline.communicate(input=parser_output)[0]

	return extract_hypotheses(henry_output)

if "__main__" == __name__: main()