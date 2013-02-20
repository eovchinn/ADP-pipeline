#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs

#inputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.txt"
#outputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.dash.txt"

semiSpace=u"‌"
inputFile=codecs.open(sys.argv[1], encoding='utf-8') if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w") if len(sys.argv)>2 else codecs.getreader("utf-8")(sys.stdout)

line=inputFile.readline()
while line!="":
    if "<META>" in line:
        line="%s."%line
    newLine=line.replace(semiSpace,"-").strip()
    outputFile.write(("%s\n"%newLine).encode('utf-8'))
    line=inputFile.readline()

inputFile.close()
outputFile.close()