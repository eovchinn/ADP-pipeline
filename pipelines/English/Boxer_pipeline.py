#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import os
from subprocess import Popen, PIPE, STDOUT

BOXER_DIR = os.environ['BOXER_DIR']

def main():
	parser = argparse.ArgumentParser( description="Boxer pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", default=None )
	parser.add_argument( "--outputdir", help="The output directory.", default=None )
	parser.add_argument( "--tok", help="Tokenize input text.", action="store_true", default=False)
	parser.add_argument( "--fname", help="File prefix for intermediate output.", default=None)
	pa = parser.parse_args()
	
	outputdir = pa.outputdir
	fname = pa.fname
	if not fname : fname = 'tmp' 

	# tokenize
	if pa.tok:
		if pa.input : 
			tokenizer = BOXER_DIR + '/bin/tokkie --input ' + pa.input
			tokenizer_proc = Popen(tokenizer, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
			tok_output = tokenizer_proc.communicate()[0]
		else : 
			tokenizer = BOXER_DIR + '/bin/tokkie --stdin'
			tokenizer_proc = Popen(tokenizer, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
			tok_output = tokenizer_proc.communicate(input=sys.stdin.read())[0]		
		
		if outputdir:	
			f_tok = open(os.path.join(outputdir,fname+".tok"), "w")
			f_tok.write(tok_output)
			f_tok.close()

	# parse
	if pa.tok:
		candcParser = BOXER_DIR + '/bin/candc --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
		candc_proc = Popen(candcParser, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)	
		candc_output = candc_proc.communicate(input=tok_output)[0]
	else:
		if pa.input :
			candcParser = BOXER_DIR + '/bin/candc --input ' + pa.input + ' --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'
			candc_proc = Popen(candcParser, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)	
			candc_output = candc_proc.communicate()[0]
		else:
			candcParser = BOXER_DIR + '/bin/candc --models ' + BOXER_DIR + '/models/boxer --candc-printer boxer'	
			candc_proc = Popen(candcParser, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)	
			candc_output = candc_proc.communicate(input=sys.stdin.read())[0]
	
	if outputdir:
		f_candc = open(os.path.join(outputdir,fname+".ccg"), "w")
		f_candc.write(candc_output)
		f_candc.close()
					
	boxer = BOXER_DIR + '/bin/boxer --semantics tacitus --resolve true --stdin'
	boxer_proc = Popen(boxer, shell=True, stdin=PIPE, stdout=PIPE, stderr=None, close_fds=True)
	boxer_output = boxer_proc.communicate(input=candc_output)[0]

	sys.stdout.write(boxer_output)

if "__main__" == __name__: main()