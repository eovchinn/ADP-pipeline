#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Ekaterina Ovchinnikova <katya@isi.edu> (2012)

# Multilinguial (English, Spanish, Farsi, Russian) abductive discource processing pipeline.
# External tools used:
#   -- English NLP pipeline (https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/English)
#   -- Spanish NLP pipeline (https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Spanish)
#   -- Russian NLP pipeline (https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Spanish)
#   -- Farsi NLP pipeline (https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Farsi)
#   -- Henry abductive reasoner (https://github.com/naoya-i/henry-n700)

# Requires env vars METAPHOR_DIR, HENRY_DIR, TMP_DIR to be set.

# In order to see options, run
# $ python NLPipeline_MULT_stdinout.py -h

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

# Compiled knowledge bases
# EN_KBPATH = "%s/KBs/English/English_compiled_KB.da" % METAPHOR_DIR
# ES_KBPATH = "%s/KBs/Spanish/Spanish_compiled_KB.da" % METAPHOR_DIR
# RU_KBPATH = "%s/KBs/Russian/Russian_compiled_KB.da" % METAPHOR_DIR
# FA_KBPATH = "%s/KBs/Farsi/Farsi_compiled_KB.da" % METAPHOR_DIR

def generate_proofgraph(id,fname,graph_input,henry_output,outputdir):
	viz = 'python ' + HENRY_DIR + '/tools/proofgraph.py' + graph_input + ' --graph ' + id + ' | dot -T pdf > ' + os.path.join(outputdir,fname+'_'+id+'.pdf')
     	graphical_proc = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)

	# Use henry output as input
     	if henry_output: graphical_proc.communicate(input=henry_output)
	# Use input file as input
	else: graphical_proc.communicate()

def main():
	parser = argparse.ArgumentParser(description="Multilinguial (English, Spanish, Farsi, Russian) abductive discource processing pipeline." )
	parser.add_argument( "--lang", help="Input language: EN, ES, RU, FA.", default='EN')
	parser.add_argument( "--input", help="Input file: plain text (possibly with text ids), observation file, henry file.", default=None )
	parser.add_argument( "--outputdir", help="Output directory. If input file defined, then default is input file dir. Otherwise its TMP_DIR.", default=None )
	parser.add_argument( "--parse", help="Tokenize and parse text, produce logical forms, convert to obeservations.", action="store_true", default=False )
	parser.add_argument( "--henry", help="Process observations with Henry.", action="store_true", default=False )
	parser.add_argument( "--kb", help="Path to noncompiled knowledge base.", default=None )
	parser.add_argument( "--kbcompiled", help="Path to compiled knowledge base.", default=None)
	parser.add_argument( "--graph", help="ID of text/sentence to vizualize. Possible value: allN, where N is number of sentences to vizualize.", default=None )
	parser.add_argument( "--textid", help="Meta text ids.", action="store_true", default=False )
	
	pa = parser.parse_args()

	# set file name prefix for output files
	fname = os.path.splitext(os.path.basename(pa.input))[0] if pa.input else 'output'
	
	# set output directory
	if pa.outputdir : outputdir = pa.outputdir
	elif pa.input: outputdir = os.path.dirname(pa.input)
	else: outputdir=TMP_DIR

	# set operating system
	if sys.platform.lower().startswith('linux'): OS = 'linux'
	elif sys.platform.lower().startswith('darwin'): OS = 'darwin'
	else: 
		print 'Unknown operating system: ' + sys.platform + '\n'
		return
	
	PARSER_PIPELINE = ''
	LF2HENRY = ''
	NONMERGE_OPTIONS = ' --nonmerge sameid freqpred'

        # Parser pipeline
	if pa.parse:
		# Parsing and generating logical forms		
		if pa.lang == 'FA':
			PARSER_PIPELINE = FARSI_PIPELINE 	
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY
		elif pa.lang == 'ES': 
			PARSER_PIPELINE = SPANISH_PIPELINE
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY
		elif pa.lang == 'RU': 
			PARSER_PIPELINE = RUSSIAN_PIPELINE
			if pa.input: 
				PARSER_PIPELINE += ' ' + pa.input + ' ' + outputdir
			LF2HENRY = 'python ' + PARSER2HENRY 
		elif pa.lang == 'EN':	
			PARSER_PIPELINE = 'python ' + ENGLISH_PIPELINE	+ ' --tok ' + '--outputdir ' + outputdir + ' --fname ' + fname
			if pa.input: 
				PARSER_PIPELINE += ' --input ' + pa.input
			LF2HENRY = 'python ' + BOXER2HENRY

		parser_proc = Popen(PARSER_PIPELINE, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
		# If there is an input file, it is passed as a parameter to the parsing pipeline		
		if pa.input:
			parser_output = parser_proc.communicate()[0]
		# If there is no input file, parsing pipeline reads from the stdin
		else: 
			parser_output = parser_proc.communicate(input=sys.stdin.read())[0]

		# Save logical forms output by the parsing pipeline
		f_par = open(os.path.join(outputdir,fname+".par"), "w")
		f_par.write(parser_output)
		f_par.close()

		# Add LF2PARSER options
		if pa.textid: LF2HENRY += ' --textid'
		LF2HENRY += NONMERGE_OPTIONS

		# Convert logical forms to henry input (observations)
		lf2h_proc = Popen(LF2HENRY, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
		nl_output = lf2h_proc.communicate(input=parser_output)[0]

		# Save observations
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

		if OS=='linux':
			HENRY = HENRY_DIR + '/bin/henry -m infer' + henry_input + ' -e ' + HENRY_DIR + '/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T 60'
		elif OS=='darwin':
			HENRY = HENRY_DIR + '/bin/henry -m infer -d 3 -t 4 -O proofgraph,statistics -T 60 -e  '+ HENRY_DIR + '/models/h93.py ' + henry_input		

		if pa.kbcompiled: HENRY += ' -b ' + pa.kbcompiled 

		henry_proc = Popen(HENRY, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)

		# Noncompiled kb specified; it is used as input parameter along with input observation file
		if pa.kb: henry_output = henry_proc.communicate()[0]
		# Noncompiled kb not specified; parsing done; parsing output is used as input
		elif pa.parse: henry_output = henry_proc.communicate(input=nl_output)[0]
		# Noncompiled kb not specified; parsing not done; input file is used as input parameter
		elif pa.input: henry_output = henry_proc.communicate()[0]
		# Noncompiled kb not specified; parsing not done; input file not specified; stdin used as input
		else: henry_output = henry_proc.communicate(input=sys.stdin.readline())[0]
		
		# Save henry output
		f_henry = open(os.path.join(outputdir,fname+".hyp"), "w")
		f_henry.write(henry_output)
		f_henry.close()

       # Graphical output
	if pa.graph:
		# Parse possible 'allN' value 
		matchObj = re.match(r'all(\d+)', pa.graph, re.M|re.I)
		
		# Henry inference done then use henry output as input		
		if not pa.henry and pa.input: 
			graph_input = ' --input ' + pa.input
			henry_output = None
		else: graph_input = ''

		# Generate proofgraphs for all sentences/texts with ids ranging from 1 to N
		if matchObj:
			for i in range(1, int(matchObj.group(1))+1):
				generate_proofgraph(str(i),fname,graph_input,henry_output,outputdir)
		# Generate proofgraph for specific sentence/text
		else:
			generate_proofgraph(pa.graph,fname,graph_input,henry_output,outputdir)

if "__main__" == __name__: main()
