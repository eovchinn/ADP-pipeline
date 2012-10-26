import sys
import codecs
inputFile=codecs.open(sys.argv[1], encoding='utf-8')
outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w")
translitDictFile=codecs.open(sys.argv[3], encoding='utf-8')



#this is a global dict for easy handling of different POS schema
POSDict={"N":"N","V":"V","AJ":"AJ","ADV":"ADV","P":"P","PR":"PR"}
postFixDict={"N":"-nn","V":"-vb","AJ":"-adj","ADV":"-rb","P":"-in","":""}
argDict={"N":2,"V":4,"AJ":2,"ADV":2,"P":3,"PR":2,"":1}
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
        if lemma[i] not in transLitDict:
            print lemma[i]
            for key in transLitDict:
                print key
            niloo=1
        englishStr+=transLitDict[lemma[i]]
    return englishStr


#farsiLitSet=set()
#def getTranslit(lemma):
#    global farsiLitSet
#    for i in range(0,len(lemma)):
#        farsiLitSet.add(lemma[i])
        
    

def propToString(prop):
    (tokenId,lemma,POS,args)=prop
    postfix=""
    if POS in postFixDict: postfix=postFixDict[POS]
    token="[%s]:%s%s(%s)"%(tokenId,getTranslit(lemma),postfix,",".join(args))
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
        
        
unknownargCounter=0
entityArgCounter=0
eventualityArgCounter=0

loadtranslitDict(translitDictFile)


wordLine=inputFile.readline()
sentenceId=1
while wordLine!="":
    words=wordLine.split()
    
    eof=False
    while len(words)==0:
        wordLine=inputFile.readline()
        if wordLine=="":
            eof=True
            break
        words=wordLine.split()
    if eof:
        break    
    POSs=inputFile.readline().split()
    print POSs
    labels=inputFile.readline().split()
    deps=inputFile.readline().split()
    
    props=[]
    for i in range(0,len(words)):
        tokenId=sentenceId*1000+(i+1)
        word=words[i]
        lemma=getLemma(word)
        POS=POSs[i]
        if POS=="PR":
            niloo=1
       
        props+=[(tokenId,lemma,POS,getArgs(POS))]
    
    PropStrings=[propToString(prop) for prop in props]    
    lfLine=" & ".join(PropStrings)
    outputFile.write("% "+" ".join(words)+"\n")
    outputFile.write("id(%s).\n"%sentenceId)
    outputFile.write("%s\n"%lfLine)
     
    wordLine=inputFile.readline()
    sentenceId+=1
    
inputFile.close()
outputFile.close()

#tempFile.write("\n".join(farsiLitSet))    
#tempFile.close()
