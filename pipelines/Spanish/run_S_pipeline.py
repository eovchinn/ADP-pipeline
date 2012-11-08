#!/usr/bin/python
# -*- coding: utf-8 -*-

import NLPipeline_Spanish_metaphor
from NLPipeline_Spanish_metaphor import *

if __name__ == "__main__":
	metaphors = {'id2': 'llevándose por delante los andamios del Estado del Bienestar','id4': 'Aquí está el PRI en pie de lucha.  Juárez siempre fue un faro que iluminó el camino de la legalidad y de la justicia.'}
	print Spanish_ADP(metaphors)
