#!/usr/bin/python

import json

import NLPipeline_coref_English_metaphor
from NLPipeline_coref_English_metaphor import *

if __name__ == "__main__":
	output_struc = English_ADP("<META>'5'\n\n Every student reads.\n\n<META>'3'\n\n This dog runs. The animal is funny.")
	print json.dumps(output_struc) 