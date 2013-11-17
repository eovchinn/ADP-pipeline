#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
import os
import re

#inputFormat: Each sentence is in a line:
#    word1_POS1 word2_POS2 ...
#outputFormat: Each token is in a line. Sentences are separated by a blank line
#    each line contains these 10 items, separated by tab: 
#    (id,word,lemma,CoarsePOS,FinePOS,etc1,dep,rel,etc2,etc3)

inputFile=codecs.open(sys.argv[1],encoding='utf-8') if len(sys.argv)>1 else codecs.getreader("utf-8")(sys.stdin)
outputFile=codecs.open(sys.argv[2],encoding='utf-8',mode="w") if len(sys.argv)>2 else codecs.getreader("utf-8")(sys.stdout)

#tmpFile=codecs.open("/temp/testdelme.txt",encoding='utf-8',mode="w")

metaphorDir=os.environ['METAPHOR_DIR']
lemmaFile=codecs.open("%s/pipelines/Farsi/lemmatizationDict.txt"%metaphorDir, encoding='utf-8')
#testLemmaFile=codecs.open("%s/pipelines/Farsi/testLemmatizationDict.txt"%metaphorDir,encoding='utf-8',mode="w")

#pronounList=[u'\u0627\u0634',u'\u062a\u0627\u0646',u'\u0627\u0645',u'\u062a',u'\u0634',u'\u0634\u0627\u0646',u'\u0645\u0627\u0646',u'\u0645',u'\u0627\u062a']

# nondashPostFixes are used for identifying postfixes that are attached to the word without dash.
nonDashPostFixes={u"ا":[u"یم",u"یت",u"یش",u"یمان",u"یتان",u"یشان",u"یی"],u"و":[u"یم",u"یت",u"یش",u"یمان",u"یتان",u"یشان",u"یی"],"":[u"م",u"ت",u"ش",u"مان",u"تان",u"شان",u"ها",u"های",u"هایی",u"هایم",u"هایت",u"هایمان",u"هایتان",u"هایشان",u"ی"]}
adjPostFixes=[u"تر",u"ترین",u"تران",u"ترها",u"ترینها",u"ترهای",u"ترینهای",u"ترانی",u"ترینهایی",u"ترینی",u"ترانی",u"تری"]
POSTFIXES = [ # used for "word-postfix"
        u"ام",
        u"ات",
        u"اش",
        u"ایم",
        u"اید",
        u"اند",
        u"یم",
        u"یت",
        u"یش",
        u"یمان",
        u"یتان",
        u"یشان",
        u"ها",
        u"تر",
        u"ترین",
        u"هایم",
        u"های",
        u"هایی",
        u"هایمان",
        u"هایتان",
        u"هایت",
        u"هایش",
        u"هایشان",
        u"ای",
        u"ایم",
        u"اید",
        u"اند",
        u"ترین",
        u"تران",
        u"ترها",
        u"ترینها",
        u"ترهای",
        u"ترینهای",
        u"ترانی",
        u"ترینهایی",
        u"ترینی",
        u"ترانی",
        u"تری"
]

#POSTFIXES = [p.encode("utf-8") for p in POSTFIXES]


def loadLemmaDict(lemmaFile):
    lemmaSet=set()
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
        lemmaSet.add((POS,lemma))
        lemmaDict [(word,POS)]=lemma
        #testLemmaFile.write("%s\t%s\n"%(word,str((word,POS))))
        line=lemmaFile.readline() 
        lineNumber+=1    
    return (lemmaDict,lemmaSet)
               
def getLemma(word,POS,lemmaDict,lemmaSet):
    #first check whether the word matches word-POSTFIX , then return word
    dashIndex=-1
    for i in range(len(word)-1,-1,-1):
        if word[i]=="-": 
            dashIndex=i
            break
    if dashIndex>-1 and word[dashIndex+1:] in POSTFIXES:
        #tmpFile.write("%s\n"%word[0:dashIndex])
        return word[0:dashIndex]
    
    
    #otherwise, refer to lemmatization dict
    if (word,POS) in lemmaDict: 
        return lemmaDict[(word,POS)]
    
    #otherwise, there might be a postfix with no dash, such that the lemmatization dict does not contain it. 
    if POS=="ADJ" or POS=="adj":
        for postfix in adjPostFixes:
            return re.sub("%s$"%postfix,"",word)
    
    if POS=="N" or POS=="n": # first we handle postfixes for which we require the word to have a special end char
        for endChar in nonDashPostFixes:
            if endChar=="": continue
            for postFix in nonDashPostFixes[endChar]:
                lemma=re.sub("%s$"%postFix,"",word)
                if lemma[-1]!=endChar: continue
                # now we have a potential lemma that ends with endChar and has a postfix that fits its endchar, check whether this lemma exists in our lemmatization dict
                if (POS,lemma) in lemmaSet:
                    return lemma
    
    if POS=="N" or POS=="n": #now we handle normal postfixes 
        for postFix in nonDashPostFixes[""]:
            lemma=re.sub("%s$"%postFix,"",word)
            # now we have a potential lemma
            if (POS,lemma) in lemmaSet:
                return lemma
    
    # no lemma found, return the word itself
    return word    

(lemmaDict,lemmaSet)=loadLemmaDict(lemmaFile)
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
        lemma=getLemma(words[i],POSs[i],lemmaDict,lemmaSet)
        items=(str(i+1),words[i],lemma,POSs[i],POSs[i],"_","_","_","_","_")
        outputFile.write(("%s\n"%"\t".join(items)).encode('utf-8'))
        #outputFile.write(("%s\n"%"\t".join(items)))

    
    outputFile.write(("\n"))
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
#testLemmaFile.close()
#tmpFile.close()    


