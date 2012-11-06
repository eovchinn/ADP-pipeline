#!/usr/bin/python

import NLPipeline_coref_English_metaphor
from NLPipeline_coref_English_metaphor import *

if __name__ == "__main__":
	metaphors = {'5': 'Every student reads.', '3': 'This dog runs. The animal is funny.'}
	print English_ADP(metaphors) 