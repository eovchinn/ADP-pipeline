# -*- coding: utf-8 -*-

import sys
import codecs

inputFileName=sys.argv[1]
outputFileName=sys.argv[2]

#inputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.txt"
#outputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.dash.txt"

semiSpace=u"‌"
inputFile=codecs.open(inputFileName, encoding='utf-8')
outputFile=codecs.open(outputFileName, encoding='utf-8',mode="w")

line=inputFile.readline()
while line!="":
    newLine=line.replace(semiSpace,"-")
    outputFile.write("%s\n"%newLine)
    line=inputFile.readline()

inputFile.close()
outputFile.close()