import sys
import codecs
import re
inputFile=codecs.open(sys.argv[1], encoding='utf-8')
outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w")
translitDictFile=codecs.open(sys.argv[3], encoding='utf-8')

#each rule is in the form "relationName":(headArgIndex,dependentArgIndex)
rules={"SBJ":(1,1),"OBJ":(2,1),"NPOSTMOD":(1,1)}


#this is a global dict for easy handling of different POS schema
POSStopList=["PUNC"]
POSDict={"N":"N","V":"V","ADJ":"ADJ","ADV":"ADV","PREP":"PREP","PR":"PR"}
postFixDict={"N":"-nn","V":"-vb","ADJ":"-adj","ADV":"-rb","PREP":"-in","":""}
argDict={"N":2,"V":4,"ADJ":2,"ADV":2,"PREP":3,"PR":2,"":1}
transLitDict={}
#tempFile=codecs.open("%s.tmp.txt"%sys.argv[3], encoding='utf-8',mode='w')


def loadtranslitDict(translitDictFile):
    lines=translitDictFile.readlines()
    for line in lines:
        (farsi,english)=line.split()
        if english =="-":english=""
        transLitDict[farsi]=english
    

def getTranslit(lemma):
    englishStr=""
    for i in range(0,len(lemma)):
#        if lemma[i] not in transLitDict:
#            print lemma[i]
#            for key in transLitDict:
#                print key
#            niloo=1
        translit=lemma[i]
        if lemma[i] in transLitDict:
            translit=transLitDict[lemma[i]]
        englishStr+=translit
    return englishStr


#farsiLitSet=set()
#def getTranslit(lemma):
#    global farsiLitSet
#    for i in range(0,len(lemma)):
#        farsiLitSet.add(lemma[i])
        
    

def propToString(sentenceId,prop):
    (id,word,lemma,POS,args)=prop
    postfix=""
    if POS in postFixDict: postfix=postFixDict[POS]
    token="[%s]:%s%s(%s)"%(sentenceId*1000+id,getTranslit(lemma),postfix,",".join(args))
    return token
    
def getLemma(word):
    return word


def getArgs(POS):
    
    global unknownargCounter
    global entityArgCounter
    global eventualityArgCounter
    args=[]
    
    args+=["e%s"%eventualityArgCounter]
    eventualityArgCounter+=1
    
    if POS in POSDict and POSDict[POS]=="N":
        
        args+=["x%s"%entityArgCounter]
        entityArgCounter+=1
        
    else:
        
        args+=["u%s"%unknownargCounter]
        unknownargCounter+=1
    
    key=""
    if POS in POSDict: key= POSDict[POS]    
    for i in range(2,argDict[key]):
        args+=["u%s"%unknownargCounter]
        unknownargCounter+=1
   
    return args 
  
def createPropDict(props):
    propDict={}
    for prop in props:
        (id,word,lemma,POS,args)=prop
        propDict[id]=prop
    return propDict

def convertSetsToLists(EqualArgMap):
    returnList=[]
    for equalSet in EqualArgMap:
        returnList+=[sorted(list(equalSet))]
    return returnList
        
def getRepresentativeArgName(equalList):
    for argName in equalList:
        if re.match("x.*",argName):
            return argName
        if re.match("e.*",argName):
            return argName
    return equalList[0]

def resolveArgs(LF):
    (sentenceId,props,rels)=LF
    propDict=createPropDict(props)
    equalArgMap=[]
    for rel in rels:
        (relName,dependent,head)=rel
        
        if relName not in rules:
            continue
              
        (headArgIndex,dependentArgIndex)=rules[relName]
        
        headProp=propDict[head]
        (headId,headWord,headLemma,headPOS,headArgs)=headProp
        
        dependentProp=propDict[dependent]
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
        
        headArgName=headArgs[headArgIndex]
        dependentArgName=dependentArgs[dependentArgIndex]
        
        foundSet=None
        for equalitySet in equalArgMap:
            if headArgName in equalitySet or dependentArgName in equalitySet:
                foundSet=equalitySet
                break
        if foundSet==None:
            foundSet=set()
            equalArgMap+=[foundSet]
        foundSet.add(headArgName)
        foundSet.add(dependentArgName)
    
    equalArgMap=convertSetsToLists(equalArgMap)
            
    for prop in props:
        (Id,Word,Lemma,POS,Args)=prop
        for i in range(0,len(Args)):
            for equalSet in equalArgMap:
                if Args[i] in equalSet:
                    Args[i]=getRepresentativeArgName(equalSet)
        
    return (sentenceId,props,rels)        
        
                
            
        
    
     
def createLF(tokens,sentenceId):
    props=[]
    rels=[]
    for token in tokens:
        (id,word,lemma,POS,relName,dep)=token
        if POS in POSStopList:
            continue
        props+=[(id,word,lemma,POS,getArgs(POS))]
        rels+=[(relName,id,dep)]
    LF=(sentenceId,props,rels)
    LF2=resolveArgs(LF)
    return LF2

def lfToString(lf):
    (sentenceId,props,rels)=lf
    words=[]
    PropStrings=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        words+=[word]
        PropStrings+=[propToString(sentenceId,prop)]
    lfLine=" & ".join(PropStrings)
    returnString= "%s\nid(%s).\n%s\n"%(" ".join(words),str(sentenceId),lfLine)
    returnString="% "+returnString
    return returnString
        
unknownargCounter=0
entityArgCounter=0
eventualityArgCounter=0

loadtranslitDict(translitDictFile)


line=inputFile.readline()
sentenceId=1
tokens=[]

while line!="":
    if line.strip()=="":   
        #one sentence read, process it and output it
        lf=createLF(tokens,sentenceId)
        outputFile.write(lfToString(lf))
#        sys.stdout.write(lfToString(lf).encode("utf-8"))
        tokens=[]
        sentenceId+=1
    else:
        a=line.split("\t")
        if len(a)!=10:
            line=inputFile.readline()
            continue
        #id,word,lemma,CoarsePOS,FinePOS,etc1,dep,relName,etc2,etc3
        id=int(a[0])
        CoarsePOS=a[-7]
        relName=a[-3]
        dep=int(a[-4])
        lemma=a[-8]
        word="-".join(" ".join(a[1:-8]).split())
        tokens+=[(id,word,lemma,CoarsePOS,relName,dep)]
        
    line=inputFile.readline()
inputFile.close()
outputFile.close()

