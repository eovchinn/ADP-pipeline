#! /usr/bin/python
# coding: utf-8

import sys
import codecs

#inputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.txt"
#outputFileName="/Users/niloofar/Metaphor-ADP/pipelines/Farsi/samples/sentence.dash.txt"

semiSpace=u"‌"
semiSpace=semiSpace.encode("utf-8")
#inputFile=codecs.open(sys.argv[1], encoding='utf-8') if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
#outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w") if len(sys.argv)>2 else codecs.getreader("utf-8")(sys.stdout)

inputFile=sys.stdin
outputFile=sys.stdout

for line in inputFile:
    if "<META>" in line:
        line="%s."%line
    newLine=line.replace(semiSpace,"-")
    outputFile.write(newLine)

