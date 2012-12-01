#! /usr/bin/python
import sys
import codecs
inputFile=codecs.open(sys.argv[1],encoding="utf-8") if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
outputFile=codecs.open(sys.argv[2],encoding="utf-8",mode="w") if len(sys.argv)>2 else codecs.getwriter("utf-8")(sys.stdout)

tokens=[]

line=inputFile.readline()
while(line!="" and line.strip()==""):
    line=inputFile.readline()
#we got a valid token
while line!="":
    token=line.strip()
    tokens+=[token]
    
    line=inputFile.readline()
    if line!="" and line.strip()=="":
        outputFile.write(("%s"%" ".join(tokens)).encode('utf-8'))
        tokens=[]
        while(line!="" and line.strip()==""):
            line=inputFile.readline()

outputFile.write(("%s"%" ".join(tokens)).encode('utf-8'))

inputFile.close()
outputFile.close()

