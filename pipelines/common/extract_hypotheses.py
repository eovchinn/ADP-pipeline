#!/usr/bin/python

import os
import sys
import re
import json
from collections import defaultdict


def main():
	output_struc = defaultdict(dict)	

	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''
	hypothesis = ''
	unification = False
	explanation = False

	for line in sys.stdin:
		matchObj = p.match(line)
		if matchObj: target = matchObj.group(1)	
		elif line.startswith('<hypothesis'): hypothesis_found = True
		elif line.startswith('</hypothesis>'): hypothesis_found = False 
		elif hypothesis_found: hypothesis = line
		elif line.startswith('<unification'): unification = True
		elif line.startswith('<explanation'): explanation = True
		elif line.startswith('</result-inference>'):
			output_struc[target]['abductive_hypothesis'] = hypothesis
			output_struc[target]['abductive_unification'] = unification
			output_struc[target]['abductive_explanation'] = explanation
			target = ''
			unification = False
			explanation = False

	final_output = json.dumps(output_struc)
	print final_output

if "__main__" == __name__: main()