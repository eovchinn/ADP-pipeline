import sys
import codecs
inputFile=codecs.open(sys.argv[1], encoding='utf-8')
outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w")
translitDictFile=codecs.open(sys.argv[3], encoding='utf-8')



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
        
    

def propToString(sentenceId,prop):
    (id,word,lemma,POS,dep,rel,args)=prop
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
 
def createLF(tokens,sentenceId):
    props=[]
    for token in tokens:
        (id,word,lemma,POS,dep,rel)=token
        if POS in POSStopList:
            continue
        props+=[(id,word,lemma,POS,dep,rel,getArgs(POS))]
    return (sentenceId,props)

def lfToString(lf):
    (sentenceId,props)=lf
    words=[]
    PropStrings=[]
    for prop in props:
        (id,word,lemma,POS,dep,rel,args)=prop
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
#        outputFile.write(lfToString(lf))
        sys.stdout.write(lfToString(lf).encode("utf-8"))
        tokens=[]
        sentenceId+=1
    else:
        a=line.split("\t")
        if len(a)!=10:
            line=inputFile.readline()
            continue
        #id,word,lemma,CoarsePOS,FinePOS,etc1,dep,rel,etc2,etc3
        id=int(a[0])
        CoarsePOS=a[-7]
        rel=a[-3]
        dep=a[-4]
        lemma=a[-8]
        word="-".join(" ".join(a[1:-8]).split())
        tokens+=[(id,word,lemma,CoarsePOS,dep,rel)]
        
    line=inputFile.readline()
inputFile.close()
outputFile.close()

