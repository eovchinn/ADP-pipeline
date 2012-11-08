'''
Created on Nov 7, 2012

@author: niloofar
'''
import sys
import codecs
inputFile=codecs.open(sys.argv[1],encoding="utf-8")
outputFile=codecs.open(sys.argv[2],encoding="utf-8",mode="w")

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
        outputFile.write("%s\n"%" ".join(tokens))
        tokens=[]
        while(line!="" and line.strip()==""):
            line=inputFile.readline()

outputFile.write("%s\n"%" ".join(tokens))

inputFile.close()
outputFile.close()

