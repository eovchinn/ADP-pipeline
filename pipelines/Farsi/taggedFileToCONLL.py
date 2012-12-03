#! /usr/bin/python

import sys
import codecs
import os

#inputFormat: Each sentence is in a line:
#    word1_POS1 word2_POS2 ...
#outputFormat: Each token is in a line. Sentences are separated by a blank line
#    each line contains these 10 items, separated by tab: 
#    (id,word,lemma,CoarsePOS,FinePOS,etc1,dep,rel,etc2,etc3)

inputFile=codecs.open(sys.argv[1],encoding='utf-8') if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
outputFile=codecs.open(sys.argv[2],encoding='utf-8',mode="w") if len(sys.argv)>2 else codecs.getreader("utf-8")(sys.stdout)


metaphorDir=os.environ['METAPHOR_DIR']
lemmaFile=codecs.open("%s/pipelines/Farsi/lemmatizationDict.txt"%metaphorDir, encoding='utf-8')


def loadLemmaDict(lemmaFile):
    lemmaDict={}
    line=lemmaFile.readline()
    while line!="":  
        if line.strip()=="":
            line=lemmaFile.readline() 
            continue
        (word,POS,lemma)=line.strip().split("\t")
        lemmaDict [(word,POS)]=lemma
        line=lemmaFile.readline() 
    return lemmaDict
def getLemma(word,POS,lemmaDict):
    if (word,POS) not in lemmaDict: return word
    return lemmaDict[(word,POS)]

lemmaDict=loadLemmaDict(lemmaFile)
line=inputFile.readline()
while line!="":
    words=[]
    POSs=[]
    wordPOSs=line.split()
    
    for wordPOS in wordPOSs:
        WordPos=wordPOS.split("_")
        if len(WordPos)>2:
            POS=WordPos[-1]
            word="_".join(WordPos[0:-1])
            
        else:(word,POS)=WordPos
        words+=[word]
        POSs+=[POS]
    for i in range(0,len(words)):
        lemma=getLemma(words[i],POSs[i],lemmaDict)
        items=(str(i+1),words[i],lemma,POSs[i],POSs[i],"_","_","_","_","_")
        outputFile.write(("%s\n"%"\t".join(items)).encode('utf-8'))
    
    outputFile.write(("\n").encode('utf-8'))
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
    


