#! /usr/bin/python
import sys
import codecs
import os



inputFile=codecs.open(sys.argv[1],encoding='utf-8') if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
outputFile=codecs.open(sys.argv[2],encoding='utf-8',mode="w") if len(sys.argv)>2 else codecs.getreader("utf-8")(sys.stdout)

metaphorDir=os.environ['METAPHOR_DIR']

line=inputFile.readline()
while line!="":
    if  line.strip() =="":
        line=inputFile.readline()
        continue
    words=line.strip().split(" ")
    #outputFile.write(str(words))
    if words[-1][-1] not in [".",";",":",",","?","!"] : words+=["."]
    
    outputFile.write(("%s\n"%" ".join(words)).encode('utf-8'))
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
    


