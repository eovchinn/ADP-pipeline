#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
from subprocess import Popen, PIPE, STDOUT

METAPHOR_DIR = os.environ['METAPHOR_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
BOXER_DIR = os.environ['BOXER_DIR']
TMP_DIR = os.environ['TMP_DIR']

FARSI_PIPELINE = "%s/pipelines/Farsi/LF_Pipeline" % METAPHOR_DIR
SPANISH_PIPELINE = "%s/pipelines/Spanish/run_spanish.sh" % METAPHOR_DIR
RUSSIAN_PIPELINE = "%s/pipelines/Russian/run_russian.sh" % METAPHOR_DIR

BOXER2HENRY = "%s/pipelines/English/Boxer2Henry.pl" % METAPHOR_DIR
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR

# Knowledge base
KBPATH = ''

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

def generate_text_input(input_dict,language):
	output_str = ''
	for id in input_dict.keys():
		if language == 'EN': output_str += "<META>'" + id + "'\n\n " + input_dict[id].replace("\u2019", "'") + "\n\n"
		else: output_str += '.TEXTID('+id+').\n\n'+input_dict[id].replace("\u2019", "'") + "\n\n" 
	return output_str	

def ADP(input_dict,language):
	start_time = time.time()
	input_str = generate_text_input(input_dict,language)

       # Run parser pipeline
	parser_proc = ''
	if language == 'FA': 
		parser_proc = FARSI_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge --textid'
	elif language == 'ES': 
		parser_proc = SPANISH_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge --textid'
	elif language == 'RU': 
		parser_proc = RUSSIAN_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge --textid'
	elif language == 'EN':
		tokenizer = BOXER_DIR + '/bin/tokkie --stdin'
		candcParser = BOXER_DIR + '/bin/candc --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
		boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --stdin'
		b2h = 'perl ' + BOXER2HENRY + ' --nonmerge sameargs'
		parser_proc = tokenizer + ' | ' + candcParser + ' | ' + boxer + ' | ' + b2h

	parser_pipeline = Popen(parser_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	parser_output = parser_pipeline.communicate(input=input_str)[0]

	parser_time = (time.time()-start_time)*0.001			# Parser processing time in seconds
	time_all_henry = 600 - parser_time		    			# all time rest for Henry in seconds	
	time_unit_henry = str(int(time_all_henry/len(input_dict)))	# time for one interpretation in Henry in seconds

	# Henry processing
	if kbcompiled:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry + ' -b ' + KBPATH 
	else:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry 

	henry_pipeline = Popen(henry_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	henry_output = henry_pipeline.communicate(input=parser_output)[0]

	return extract_hypotheses(henry_output)

if "__main__" == __name__: main()