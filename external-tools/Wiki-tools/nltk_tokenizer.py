#!/usr/bin/python
# -*- coding: utf-8 -*-

# sentence segmentor for only EN, ES and RU

import sys
import argparse
import nltk
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer


parser = argparse.ArgumentParser()
parser.add_argument('-l',dest = 'lang')
parser.add_argument('--input',dest = 'file')

pa = parser.parse_args()
lang = pa.lang
filePath = pa.file
outputPath = filePath+'.sent'
if __name__ == "__main__":    
    file = open(filePath,'r')
    output = open(outputPath,'w')
    sst = None
    if lang == 'EN':
        sst = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
    elif lang == 'ES':
        sst = nltk.data.load('nltk:tokenizers/punkt/spanish.pickle')
    else:
        sst = PunktSentenceTokenizer()
    for line in file:
        
        if line == "\n":
            sys.stdout.write(line)
            continue
        line = line.replace("«", "'")
        line = line.replace("»", "'")
        line = line.replace("“", "'")
        line = line.replace("”", "'")
        line = line.replace("\"", "'")
        sentences = sst.tokenize(line.decode("utf-8"))
        for s in sentences:
            output.write((s+'\n').encode('utf-8'))
    file.close()
    output.close()
