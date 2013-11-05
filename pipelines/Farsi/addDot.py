#! /usr/bin/python
import sys
import codecs
import os



inputFile=sys.stdin
outputFile=sys.stdout

for line in inputFile:
    if  line.strip() =="":
        continue
    words=line.strip().split(" ")
    #outputFile.write(str(words))
    if words[-1][-1] not in [".",";",":",",","?","!"] : words+=["."]
    
    outputFile.write("%s\n"%" ".join(words))
        


