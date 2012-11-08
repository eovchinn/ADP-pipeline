#!/usr/bin/python
# -*- coding: utf-8 -*-

import NLPipeline_Russian_metaphor
from NLPipeline_Russian_metaphor import *

if __name__ == "__main__":
	metaphors = {'id2':'Съешьте еще этих мягких французских булочек, да выпейте же чаю.','id4':' Небо было почти черным, а снег при свете луны – ярко-голубым. И еще одно предложение'}
	print Russian_ADP(metaphors)
