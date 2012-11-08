#!/usr/bin/python

import NLPipeline_coref_English_metaphor
from NLPipeline_coref_English_metaphor import *

if __name__ == "__main__":
	metaphors = {'5': 'Few nations have gone through what you have gone through, and few nations in recent history have made the progress you\u2019ve made.', '3': 'This dog runs. The animal is funny.'}
	print English_ADP(metaphors) 