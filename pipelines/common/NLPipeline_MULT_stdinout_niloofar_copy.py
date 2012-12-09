#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import re
from subprocess import Popen, PIPE, STDOUT

METAPHOR_DIR = os.environ['METAPHOR_DIR']
HENRY_DIR = os.environ['HENRY_DIR']
TMP_DIR = os.environ['TMP_DIR']

BOXER2HENRY = "%s/pipelines/English/Boxer2Henry.py" % METAPHOR_DIR
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR

ENGLISH_PIPELINE = "%s/pipelines/English/Boxer_pipeline.py" % METAPHOR_DIR
FARSI_PIPELINE = "%s/pipelines/Farsi/LF_Pipeline" % METAPHOR_DIR
SPANISH_PIPELINE = "%s/pipelines/Spanish/run_spanish.sh" % METAPHOR_DIR
RUSSIAN_PIPELINE = "%s/pipelines/Russian/run_russian.sh" % METAPHOR_DIR

# Compiled knowledge base
KBPATH = ''

def main():
	parser = argparse.ArgumentParser( description="Multilinguial discource processing pipeline saving intermediate output." )
	parser.add_argument( "--lang", help="Input language.", default='EN' )
	parser.add_argument( "--input", help="Input file.", default=None )
	parser.add_argument( "--outputdir", help="Output directory. If input file defined, then default is input file dir. Otherwise its TMP_DIR.", default=None )
	parser.add_argument( "--parse", help="Tokenize and parse text.", action="store_true", default=False )
	parser.add_argument( "--henry", help="Process LF with Henry.", action="store_true", default=False )
	parser.add_argument( "--kb", help="Path to noncompiled knowledge base.", default=None )
	parser.add_argument( "--kbcompiled", help="Use compiled knowledge base.", action="store_true", default=False)
	parser.add_argument( "--graph", help="ID of sentence to vizualize. Possible value: allN, where N is number of sentences to vizualize.", default=None )
	parser.add_argument( "--textid", help="Meta text ids.", action="store_true", default=False )
	
	pa = parser.parse_args()

	fname = os.path.splitext(os.path.basename(pa.input))[0] if pa.input else 'tmp'
	
	if pa.outputdir : outputdir = pa.outputdir
	elif pa.input: outputdir = os.path.dirname(pa.input)
	else: outputdir = TMP_DIR

	PARSER_PIPELINE = ''
	LF2HENRY = ''
       # Parser pipeline
	if pa.parse:
		if pa.lang == 'FA':
			PARSER_PIPELINE = FARSI_PIPELINE 	
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY + ' --nonmerge sameid freqpred'
		elif pa.lang == 'ES': 
			PARSER_PIPELINE = SPANISH_PIPELINE
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY + ' --nonmerge sameid freqpred'
		elif pa.lang == 'RU': 
			PARSER_PIPELINE = RUSSIAN_PIPELINE
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY + ' --nonmerge sameid freqpred'
		elif pa.lang == 'EN':	
			PARSER_PIPELINE = 'python ' + ENGLISH_PIPELINE	+ ' --tok ' + '--outputdir ' + outputdir + ' --fname ' + fname
			if pa.input: 
				PARSER_PIPELINE += ' --input ' + pa.input
			LF2HENRY = 'python ' + BOXER2HENRY + ' --nonmerge sameid freqpred'

		print 'COMMAND: ' + PARSER_PIPELINE

		parser_proc = Popen(PARSER_PIPELINE, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
		if pa.input:
			parser_output = parser_proc.communicate()[0]
		else: 
			parser_output = parser_proc.communicate(input=sys.stdin.readline())[0]

		f_par = open(os.path.join(outputdir,fname+".par"), "w")
		f_par.write(parser_output)
		f_par.close()

		if pa.textid: LF2HENRY += ' --textid'

		lf2h_proc = Popen(LF2HENRY, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
		nl_output = lf2h_proc.communicate(input=parser_output)[0]

		f_lf2h = open(os.path.join(outputdir,fname+".obs"), "w")
		f_lf2h.write(nl_output)
		f_lf2h.close()

	# Henry processing
	if pa.henry:
		henry_input = ''
		if pa.kb: 
			henry_input += ' ' + pa.kb
			if pa.parse: henry_input += ' ' + os.path.join(outputdir,fname+".obs")
			elif pa.input: henry_input += ' ' + pa.input
		elif (not pa.parse) and pa.input: 
			henry_input += ' ' + pa.input

		#HENRY = HENRY_DIR + '/bin/henry -m infer' + henry_input + ' -e ' + HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T 60'
		HENRY = HENRY_DIR + '/bin/henry -m infer -d 3 -t 4 -O proofgraph,statistics -T 60 -e  '+ HENRY_DIR + '/models/h93.py ' + henry_input

		if pa.kbcompiled: HENRY += ' -b ' + KBPATH 

		henry_proc = Popen(HENRY, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)

		if pa.kb: henry_output = henry_proc.communicate()[0]
		elif pa.parse: henry_output = henry_proc.communicate(input=nl_output)[0]
		elif pa.input: henry_output = henry_proc.communicate()[0]
		else: henry_output = henry_proc.communicate(input=sys.stdin.readline())[0]
		
		f_henry = open(os.path.join(outputdir,fname+".hyp"), "w")
		f_henry.write(henry_output)
		f_henry.close()

       # Graphical output
	if pa.graph:
		matchObj = re.match(r'all(\d+)', pa.graph, re.M|re.I)
		graph_input = ''
		if not pa.henry and pa.input: graph_input = ' --input ' + pa.input

		if matchObj:
			for i in range(1, int(matchObj.group(1))+1):
				viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py' + graph_input + ' --graph ' + str(i) + ' | dot -T pdf > ' + os.path.join(outputdir,fname+'_'+str(i)+'.pdf')
				graphical_proc = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
     				if pa.henry: graphical_proc.communicate(input=henry_output)
				else: graphical_proc.communicate()
		else:
			viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py' + graph_input + ' --graph ' + pa.graph + ' | dot -T pdf > ' + os.path.join(outputdir,fname+'_'+pa.graph+'.pdf')
     			graphical_proc = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
     			if pa.henry: graphical_proc.communicate(input=henry_output)
			else: graphical_proc.communicate()

if "__main__" == __name__: main()
