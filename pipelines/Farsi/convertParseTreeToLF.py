import sys
import codecs
import re
inputFile=codecs.open(sys.argv[1], encoding='utf-8')
#outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w")
#sys.stdout.setdefaultencoding('utf-8')
outputFile=sys.stdout
translitDictFile=codecs.open(sys.argv[3], encoding='utf-8')

#each rule is in the form "relationName":(headArgIndex,dependentArgIndex)
rules={"SBJ":[(1,1)],"OBJ":[(2,1)],"VCL":[(2,0)],"PRD":[(0,0)],"NPOSTMOD":[(1,1)]}

#this is a global dict for easy handling of different POS schema
POSStopList=["PUNC"]
wordStopList=["\"","'","(",")"]
POSDict={"N":"N","V":"V","ADJ":"ADJ","ADV":"ADV","PREP":"PREP","PR":"PR"}
postFixDict={"N":"-nn","V":"-vb","ADJ":"-adj","ADV":"-rb","PREP":"-in","":""}
argDict={"N":2,"V":4,"ADJ":2,"ADV":2,"PREP":3,"PR":2,"":1}
transLitDict={}
#tempFile=codecs.open("%s.tmp.txt"%sys.argv[3], encoding='utf-8',mode='w')

def findProp(props,propId):
    for prop in props:
        (id,word,lemma,POS,args)=prop
        if id==propId:
            return prop
    return None
        
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
#    print sentenceId
    if id==22:
        niloo=1
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

def convertSetsToLists(equalArgSets):
    returnList=[]
    for equalSet in equalArgSets:
        returnList+=[sorted(list(equalSet))]
    return returnList
        
def getRepresentativeArgName(equalList):
    for argName in equalList:
        if re.match("x.*",argName):
            return argName
        if re.match("e.*",argName):
            return argName
    return equalList[0]
def getEqualArgSets(propDict,rels):
    equalArgSets=[]
    for rel in rels:
        (relName,dependent,head)=rel    
        if relName not in rules:
            continue
        headProp=propDict[head]
        (headId,headWord,headLemma,headPOS,headArgs)=headProp
        
        dependentProp=propDict[dependent]
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
        
        argUnifications=rules[relName]
        for argUnification in argUnifications:      
            (headArgIndex,dependentArgIndex)=argUnification
            headArgName=headArgs[headArgIndex]
            dependentArgName=dependentArgs[dependentArgIndex]
            
            foundSet=None
            for equalitySet in equalArgSets:
                if headArgName in equalitySet or dependentArgName in equalitySet:
                    foundSet=equalitySet
                    break
            if foundSet==None:
                foundSet=set()
                equalArgSets+=[foundSet]
            foundSet.add(headArgName)
            foundSet.add(dependentArgName)
    
    equalArgSets=convertSetsToLists(equalArgSets)
    return equalArgSets

def getDependentId(rels,headId,relationName):
    for rel in rels:
        (relName1,depId1,headId1)=rel
        if relationName==relName1 and headId==headId1:
            return depId1
    return None
        
    
def getNounConjArgSets(props,rels):
    nounConjArgSets=[]
    tempList=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName== "NCONJ":
            conj1Prop=findProp(props,headId)
            conj2Id=getDependentId(rels,dependentId,"POSDEP")
            if conj2Id==None:
                continue
            conj2Prop=findProp(props,conj2Id)
            (conj1Id,conj1Word,conj1Lemma,conj1POS,conj1Args)=conj1Prop
            (conj2Id,conj2Word,conj2Lemma,conj2POS,conj2Args)=conj2Prop
            conj1Arg=conj1Args[1]
            conj2Arg=conj2Args[1]
            tempList+=[(conj1Arg,conj2Arg)]
        
    for (arg1,arg2) in tempList:
        foundSet=None
        for conjSet in nounConjArgSets:
            if arg1 in conjSet or arg2 in conjSet:
                foundSet=conjSet
                break
        if foundSet==None:
            foundSet=set()
            nounConjArgSets+=[foundSet]
        foundSet.add(arg1)
        foundSet.add(arg2)
    
    return nounConjArgSets
            
def replaceEqualArgs(props,equalArgSets):
    for prop in props:
        (Id,Word,Lemma,POS,Args)=prop
        for i in range(0,len(Args)):
            for equalSet in equalArgSets:
                if Args[i] in equalSet:
                    Args[i]=getRepresentativeArgName(equalSet)
    return props

def getMaxPropId(props):
    maxId=-1
    for prop in props:
        (Id,Word,Lemma,POS,Args)=prop
        if Id>maxId:
            maxId=Id
    return maxId
        
def addModifiers(props,rels,originalProp,newProp):
    global eventualityArgCounter
    global propIdCounter
    propIdCounter+=1
    
    (originalPropId,originalPropWord,originalPropLemma,originalPropPOS,originalPropArgs)=originalProp
    (newPropId,newPropWord,newPropLemma,newPropPOS,newPropArgs)=newProp
    
    originalPropArg0=originalPropArgs[0]
    newPropArgs0=newPropArgs[0]
    
    #we duplicate any proposition that has originalProp's 0th argument in it.
    newModifierProps=[]
#    verbModifierRels=["NVE","ENC","VPP","ADV","AJUCL"]
    for prop in props:
        (propId,word,lemma,POS,args)=prop    
        if lemma=="NVE":
            niloo=1    
        for i in range(1,len(args)):
            if args[i]==originalPropArg0: # we found a prop that has originalPropArg0 as one of its arguments -> duplicate this prop and replace the argument with new argument
                newDependentPropArgs=list(args)
                newDependentPropArgs[i]= newPropArgs0
                newDependentPropArgs[0]="e%s"%(eventualityArgCounter+1)
                eventualityArgCounter+=1
                newModifierProp=(propIdCounter+1,word,lemma,POS,newDependentPropArgs)
                propIdCounter+=1
                newModifierProps+=[newModifierProp]
    return newModifierProps
            
def createNewPropsForNounConjs(props,rels,nounConjArgSets):
    global eventualityArgCounter
    eventualityArgCounter+=1
    newProps=[]
    newModifiers=[]
    global propIdCounter
    propIdCounter+=1
    for originalProp in props:
#        print originalProp
        (originalPropId,Word,Lemma,POS,Args)=originalProp
        if POS!=POSDict["V"]:
            continue
        propArgSet=set(Args)
        
        #if any of the arguments in nounConjArgSet appears in the proposition, then we need to duplicate that proposition for any of the other elements in nounConjArgSet
        conjSets=[] # a collection of sets, each set corresponds to an argument of prop 
        for i in range(1,4): # we assume max number of arguments is 4, skip the 0th argument which is the eventuality arg
            if i>=len(Args):
                conjSets+=[set(["dummy"])]
                continue
            conjSet=set([Args[i]])
            
            for nounConjArgSet in nounConjArgSets:
                if nounConjArgSet.intersection(conjSet): #if these two sets have an overlap, add all elements from the nounConjArgSet to conjSets[i]
                    conjSet=conjSet.union(nounConjArgSet)
            conjSets+=[conjSet]
        
        for arg1 in conjSets[0]:    #remember that we don't have a conj set for the 0th argument. So the first conjSet (conjSet[0]) corresponds to the 1st arg
            for arg2 in conjSets[1]:
                for arg3 in conjSets[2]:
                    newArgs=["e%s"%eventualityArgCounter]
                    if arg1!="dummy":
                        newArgs+=[arg1]
                    if arg2!="dummy":
                        newArgs+=[arg2]
                    if arg3!="dummy":
                        newArgs+=[arg3]
                    
                    if newArgs[1:]==Args[1:]: # if same argument, don't add anything
                        continue
                    newPropId=propIdCounter+1
                    newProp=(newPropId,Word,Lemma,POS,newArgs)
                    newModifiers+=addModifiers(props,rels,originalProp,newProp)
                    newProps+=[newProp]
                    eventualityArgCounter+=1
                    propIdCounter+=1
    return props+newProps+newModifiers

def createNewPropsForLightVerbs(props,rels):
    global eventualityArgCounter
    global propIdCounter
    propIdCounter+=1
    newProps=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName in ["NVE","ENC"]:
            eventualityArgCounter+=1
            
            dependentProp=findProp(props,dependentId)
            (dependentPropId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
            
            headProp=findProp(props,headId)
            (headId,headWord,headLemma,headPOS,headArgs)=headProp
            
            newProp=(propIdCounter,"",relName,"",["e%s"%eventualityArgCounter,dependentArgs[0],headArgs[0]])
            newProps+=[newProp]
            propIdCounter+=1
            
    return props+newProps
                


        
def createLF(tokens,sentenceId):
    global propIdCounter
    props=[]
    rels=[]
    words=[]
    for token in tokens:
        (id,word,lemma,POS,relName,dep)=token
        words+=[word]
        if POS in POSStopList or word in wordStopList:
            continue
        props+=[(id,word,lemma,POS,getArgs(POS))]
        rels+=[(relName,id,dep)]
    sentence= " ".join(words)
    LF=(sentenceId,sentence,props,rels)
    propIdCounter=getMaxPropId(props)
    LF2=resolveArgs(LF)
    return LF2

def lfToString(lf):
    (sentenceId,sentence,props,rels)=lf
    words=[]
    PropStrings=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        words+=[word]
        PropStrings+=[propToString(sentenceId,prop)]
    lfLine=" & ".join(PropStrings)
    returnString= "%s\nid(%s).\n%s\n"%(sentence,str(sentenceId),lfLine)
    returnString="% "+returnString
    return returnString

def resolveArgs(LF):
    (sentenceId,sentence,props,rels)=LF
    #add new props for light verbs (add preds like NVE,ENC)
    props=createNewPropsForLightVerbs(props,rels)
    
    propDict=createPropDict(props)
    equalArgSets=getEqualArgSets(propDict,rels)    
    props=replaceEqualArgs(props,equalArgSets)
    
    nounConjArgSets=getNounConjArgSets(props,rels)
    props=createNewPropsForNounConjs(props,rels,nounConjArgSets)
           
    return (sentenceId,sentence,props,rels)               

unknownargCounter=0
entityArgCounter=0
eventualityArgCounter=0
propIdCounter=0

loadtranslitDict(translitDictFile)


line=inputFile.readline()
sentenceId=1
tokens=[]

while line!="":
    if line.strip()=="":   
        #one sentence read, process it and output it
        lf=createLF(tokens,sentenceId)
        outputFile.write(lfToString(lf).encode('utf-8'))
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
        if word=="-LRB-": word="("
        if word=="-RRB-": word=")"
        tokens+=[(id,word,lemma,CoarsePOS,relName,dep)]
        
    line=inputFile.readline()
inputFile.close()
outputFile.close()

