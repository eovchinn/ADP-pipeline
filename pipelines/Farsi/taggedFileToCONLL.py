#! /usr/bin/python
# -*- coding: utf-8 -*-
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
testLemmaFile=codecs.open("%s/pipelines/Farsi/testLemmatizationDict.txt"%metaphorDir,encoding='utf-8',mode="w")

pronounList=[u'\u0627\u0634',u'\u062a\u0627\u0646',u'\u0627\u0645',u'\u062a',u'\u0634',u'\u0634\u0627\u0646',u'\u0645\u0627\u0646',u'\u0645',u'\u0627\u062a']
#for pronoun in pronounList:
#    print (pronoun,"PRO")
niloo=1

def loadLemmaDict(lemmaFile):
    lemmaDict={}
    line=lemmaFile.readline()
    lineNumber=1
    while line!="":  
        if line.strip()=="":
            line=lemmaFile.readline()
            lineNumber+=1 
            continue
#        print lineNumber
        (word,POS,lemma)=line.replace(u'\u200e',"").strip().split("\t")
        lemmaDict [(word,POS)]=lemma
        testLemmaFile.write("%s\t%s\n"%(word,str((word,POS))))
        line=lemmaFile.readline() 
        lineNumber+=1
    
    addLemmaForWordsWithpossesivePostFix(lemmaDict)
    return lemmaDict
def addLemmaForWordsWithpossesivePostFix(lemmaDict):
    #maybe our combination is not in lemmatization dict, try decomposing the word
    #if the word ends with a pronoun, then replace the pronoun with "" and check whether the new word is in out lemmatization dict. If so, return the lemma of that new word
    newItems={}
    for (lemma,POS)in lemmaDict:
        if lemma==u'\u0627\u0647\u062f\u0627\u0641':
            niloo=1
        for pronoun in pronounList:
            newItems[("%s%s"%(lemma,pronoun.replace(u'\u200e',"")),POS)]=lemma
    for key in newItems:
        lemmaDict[key]=newItems[key]
                
def getLemma(word,POS,lemmaDict):
    if (word,POS) not in lemmaDict: 
#        print "NILOO:%s\t%s"%(word,str((word,POS)))
        return word
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
        #outputFile.write(("%s\n"%"\t".join(items)))

    
    outputFile.write(("\n"))
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
testLemmaFile.close()
    


