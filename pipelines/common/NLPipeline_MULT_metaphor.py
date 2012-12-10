#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import thread
import socket
from subprocess import Popen, PIPE, STDOUT

METAPHOR_DIR = os.environ['METAPHOR_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
BOXER_DIR = os.environ['BOXER_DIR']
TMP_DIR = os.environ['TMP_DIR']

FARSI_PIPELINE = "%s/pipelines/Farsi/LF_Pipeline" % METAPHOR_DIR
SPANISH_PIPELINE = "%s/pipelines/Spanish/run_spanish.sh" % METAPHOR_DIR
RUSSIAN_PIPELINE = "%s/pipelines/Russian/run_russian.sh" % METAPHOR_DIR

BOXER2HENRY = "%s/pipelines/English/Boxer2Henry.py" % METAPHOR_DIR
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR

# Compiled knowledge bases
EN_KBPATH = "%s/KBs/English/English_compiled_KB.da" % METAPHOR_DIR
ES_KBPATH = "%s/KBs/Spanish/Spanish_compiled_KB.da" % METAPHOR_DIR
RU_KBPATH = "%s/KBs/Russian/Russian_compiled_KB.da" % METAPHOR_DIR
FA_KBPATH = "%s/KBs/Farsi/Farsi_compiled_KB.da" % METAPHOR_DIR

# switches
kbcompiled = True

#unique_id used for proofgraph name (annotation_id may not be enough, as
#different docs may have same annotation_ids)
#withPDFContent=true; generate graphs and include PDF content as base-64 in output
def extract_hypotheses(inputString,unique_id,withPDFContent):
	output_struct = []
	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''
	hypothesis = ''
	unification = False
	explanation = False

	#for generating proofgraph URIs
	webservice=get_webservice_location()

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
			output_struct_item['abductive_proofgraph'] = 'http://'+webservice+'/proofgraphs/'+unique_id+'_'+target+'.pdf'
			if withPDFContent:
                           output_struct_item['abductive_proofgraph_str'] = get_base64(TMP_DIR+'/proofgraphs/'+unique_id+'_'+target+'.pdf')
			output_struct_item['description'] = 'Abductive engine output; abductive_hypothesis: metaphor interpretation; abductive_unification: unifications happened or not; abductive_explanation: axioms applied or not'
			output_struct.append(output_struct_item)  
			target = ''
			unification = False
			explanation = False

	return json.dumps(output_struct,ensure_ascii=False)

def generate_text_input(input_dict,language):
	output_str = ''
	for id in input_dict.keys():
		if language == 'EN': output_str += "<META>" + id + "\n\n " + input_dict[id] + "\n\n"
		elif language == 'RU': output_str += 'TEXTID('+id+')\n\n'+input_dict[id] + "\n\n" 
		else: output_str += '.TEXTID('+id+').\n\n'+input_dict[id] + "\n\n" 
	return output_str	

#withPDFContent=true; generate graphs and include PDF content as base-64 in output
def ADP(input_dict,language,withPDFContent):
	start_time = time.time()
	input_str = generate_text_input(input_dict,language)

       # Parser pipeline
	parser_proc = ''
	if language == 'FA': 
		parser_proc = FARSI_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge sameid freqpred --textid'
		KBPATH = FA_KBPATH
	elif language == 'ES': 
		parser_proc = SPANISH_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge sameid freqpred --textid'
		KBPATH = ES_KBPATH
	elif language == 'RU': 
		parser_proc = RUSSIAN_PIPELINE  + ' | python ' + PARSER2HENRY + ' --nonmerge sameid freqpred'
		KBPATH = RU_KBPATH
	elif language == 'EN':
		tokenizer = BOXER_DIR + '/bin/tokkie --stdin'
		candcParser = BOXER_DIR + '/bin/candc --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
		boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --stdin'
		b2h = 'python ' + BOXER2HENRY + ' --nonmerge sameid freqpred'
		parser_proc = tokenizer + ' | ' + candcParser + ' | ' + boxer + ' | ' + b2h
		KBPATH = EN_KBPATH

	parser_pipeline = Popen(parser_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	parser_output = parser_pipeline.communicate(input=input_str)[0]

	parser_time = (time.time()-start_time)*0.001			# Parser processing time in seconds
	generate_output_time = 2						# time to generate final output in seconds
	time_all_henry = 600 - parser_time	- generate_output_time 	# time left for Henry in seconds	
	if withPDFContent: time_all_henry = time_all_henry - 3		# time for graph generation subtracted from Henry time in seconds
	time_unit_henry = str(int(time_all_henry/len(input_dict)))	# time for one interpretation in Henry in seconds

	# Henry processing
	if kbcompiled:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry + ' -b ' + KBPATH 
	else:
		henry_proc = HENRY_DIR + '/bin/henry -m infer -e ' +  HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T ' + time_unit_henry 

	henry_pipeline = Popen(henry_proc, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	henry_output = henry_pipeline.communicate(input=parser_output)[0]

       #unique id used for proofgraph name
	unique_id = get_unique_id()

	if withPDFContent:
          #generate graphs so we can return them with output
          generate_graph(input_dict,henry_output,unique_id)		
	else:
          #start graphical generation in thread; don't wait for it to finish
          thread.start_new_thread(generate_graph, (input_dict,henry_output,unique_id))


        return extract_hypotheses(henry_output,unique_id,withPDFContent)

def get_webservice_location():
	hostname=socket.getfqdn()
	#this gives the IP address; you may want to use this during the demo
	#hostname=socket.gethostbyname(hostname)
	port='8000'
	if os.environ.get('ADP_PORT') is not None:
           port=os.environ.get('ADP_PORT')
	return hostname+":"+port

def get_unique_id():
	current_time=int(time.time())
	unique_id=str(current_time)[5:]
	return unique_id

def generate_graph(input_dict,henry_output,unique_id):
   #create proofgraphs directory if it doesn't exist
   graph_dir=TMP_DIR+'/proofgraphs' 
   if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

   for id in input_dict.keys():
     graph_output = os.path.join(graph_dir,unique_id+'_'+id+'.pdf')
     viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py --graph ' + id + ' | dot -T pdf > ' + graph_output
     graphical_processing = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
     graphical_processing.communicate(input=henry_output)
     #print "sleep"
     #time.sleep(3)
   print "Done generating proof graphs."

#returns contents of PDF file in base-64
def get_base64(pdffile):
	f=open (pdffile,"rb")
	binaryS = f.read()
	encodeS = binaryS.encode("base64")
	return encodeS


if "__main__" == __name__: main()
