import sys
import codecs
import re
inputFile=codecs.open(sys.argv[1], encoding='utf-8')
#outputFile=codecs.open(sys.argv[2], encoding='utf-8',mode="w")
#sys.stdout.setdefaultencoding('utf-8')
outputFile=sys.stdout
farsiWordsForLFFile=codecs.open(sys.argv[3], encoding='utf-8')

#each rule is in the form "relationName":(headArgIndex,dependentArgIndex)
rules={"SBJ":[(1,1)],"OBJ":[(2,1)],"NCL":[(1,1)],"PRD":[(2,0)],"NPOSTMOD":[(1,1)],"NPREMOD":[(1,1)],"ADV":[(0,1)],"POSDEP":[(2,1)],"VPP":[(0,1)],"NPP":[(1,1)],"PARCL":[(1,1)]}

#this is a global dict for easy handling of different POS schema
POSStopList=["PUNC"]
wordStopList=["\"","'","(",")"]
POSDict={"N":"N","V":"V","ADJ":"ADJ","ADV":"ADV","PREP":"PREP","PR":"PR","CONJ":"CONJ","SUBR":"SUBR"}
postFixDict={"N":"-nn","V":"-vb","ADJ":"-adj","ADV":"-rb","PREP":"-in","":""}
argDict={"N":2,"V":4,"ADJ":2,"ADV":2,"PREP":3,"PR":2,"":1,"CONJ":2,"SUBR":3}
listOfNonAlphaNumChars=["!","+","<",">","[","]","%",",","(",")","!",".","?","@","#","$","%","^","&","*","-","_","=","+","'",'"',";",":","/","\\","|","{","}","`","'"]
#tempFile=codecs.open("%s.tmp.txt"%sys.argv[3], encoding='utf-8',mode='w')
pronouns={}
pluralPostfixes=[]
transLitDict={}
conditionalList=[]
becauseList=[]
negationList=[]
#whileList=[]
def findProp(props,propId):
    global pronouns
    for prop in props:
        (id,word,lemma,POS,args)=prop
        if id==propId:
            return prop
    return None
    
def readTransliterationDict(startLineNumber,lines):
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        (farsi,english)=lines[i].split()
        if english =="-":english=""
        transLitDict[farsi]=english
    return i
        
def readPronounList(startLineNumber,lines):
    global pronouns
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
#            for pronoun in pronouns:
#                print "%s\t%s"%(pronoun,pronouns[pronoun])
            return i+1
        (pronoun,person,animate)=lines[i].split()
        pronoun=pronoun.replace(u'\u200e',"")
        pronouns[pronoun]=(pronoun,person)
    return i

def readPluralList(startLineNumber,lines):
    global pluralPostfixes
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        pluralPostfix=lines[i].strip()
        pluralPostfixes+=[pluralPostfix]
    return i
    
def readCondList(startLineNumber,lines):
    global conditionalList
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        conditional=lines[i].strip()
        conditionalList+=[conditional]
    return i

def readWhileList(startLineNumber,lines): 
    global whileList
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        whileWord=lines[i].strip()
        whileList+=[whileWord]
    return i  

def readBecauseList(startLineNumber,lines): 
    global becauseList
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        becauseWord=lines[i].strip()
        becauseList+=[becauseWord]
    return i  

def readNegationList(startLineNumber,lines):
    global negationList
    for i in range(startLineNumber,len(lines)):
        if re.match("--.*",lines[i]):
            return i+1
        negationWord=lines[i].strip()
        negationList+=[negationWord]
    return i  
    
              
def loadFarsiWordsForLFFile(farsiWordsForLFFile):
    lines=farsiWordsForLFFile.readlines()
    startLineNumber=1
    startLineNumber=readTransliterationDict(startLineNumber,lines)
    startLineNumber=readPronounList(startLineNumber,lines)
    startLineNumber=readPluralList(startLineNumber,lines)
    startLineNumber=readCondList(startLineNumber,lines)
    startLineNumber=readBecauseList(startLineNumber,lines)
    startLineNumber=readNegationList(startLineNumber,lines)
    

def getTranslit(lemma):
    englishStr=""
    for i in range(0,len(lemma)):
        translit=lemma[i]
        if lemma[i] in transLitDict:
            translit=transLitDict[lemma[i]]
        englishStr+=translit
    return englishStr

def propToString(sentenceId,prop):
    (id,word,lemma,POS,args)=prop
    postfix=""
    if POS in postFixDict: postfix=postFixDict[POS]
#    print sentenceId
    if id==-1:
        idString=""
    else:
        idString="[%s]:"%(sentenceId*1000+id)
    #token="%s%s__%s%s(%s)"%(idString,word,lemma,postfix,",".join(args))
    token="%s%s%s(%s)"%(idString,lemma,postfix,",".join(args))
    return token
    
def getArgs(POS):
    
    global unknownargCounter
    global entityArgCounter
    global eventualityArgCounter
    args=[]
    
    args+=["e%s"%eventualityArgCounter]
    eventualityArgCounter+=1
    
    if POS in POSDict and (POSDict[POS]=="N" or POSDict[POS]=="PR"):
        
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
        
        if relName=="ADV":
            niloo=1
        if head not in propDict:
            niloo=1
        headProp=propDict[head]
        (headId,headWord,headLemma,headPOS,headArgs)=headProp
        
        dependentProp=propDict[dependent]
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
        
        argUnifications=rules[relName]
        for argUnification in argUnifications:      
            (headArgIndex,dependentArgIndex)=argUnification
            if headArgIndex>=len(headArgs) or dependentArgIndex>len(dependentArgs):
                #warning
                continue
            headArgName=headArgs[headArgIndex]
            dependentArgName=dependentArgs[dependentArgIndex]
            
            if headArgName=="u2" or dependentArgName=="u2":
                niloo=1
            
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
    equalArgSets=convertSetsToLists(equalArgSets)
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
    
    (originalPropId,originalPropWord,originalPropLemma,originalPropPOS,originalPropArgs)=originalProp
    (newPropId,newPropWord,newPropLemma,newPropPOS,newPropArgs)=newProp
    
    originalPropArg0=originalPropArgs[0]
    newPropArgs0=newPropArgs[0]
    
    #we duplicate any proposition that has originalProp's 0th argument in it.
    newModifierProps=[]
#    verbModifierRels=["NVE","ENC","VPP","ADV","AJUCL"]
    for prop in props:
        (propId,word,lemma,POS,args)=prop    
        for i in range(1,len(args)):
            if args[i]==originalPropArg0: # we found a prop that has originalPropArg0 as one of its arguments -> duplicate this prop and replace the argument with new argument
                newDependentPropArgs=list(args)
                newDependentPropArgs[i]= newPropArgs0
                newDependentPropArgs[0]="e%s"%(eventualityArgCounter+1)
                eventualityArgCounter+=1
                newModifierProp=(propId,word,lemma,POS,newDependentPropArgs) #same propId
                newModifierProps+=[newModifierProp]
    return newModifierProps

def handleBecauseWords(props,rels):
    equalSet=set()
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName!="AJUCL": continue
        (headId,headWord,headLemma,headPOS,headArgs)=findProp(props,headId)
        dependentProp=findProp(props,dependentId)
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
        if dependentLemma not in becauseList:continue
        becauseDependent=getDependentId(rels,headId,"PRD")
        (becauseDependentId,becauseDependentWord,becauseDependentLemma,becauseDependentPOS,becauseDependentArgs)=becauseDependent
        equalSet.add([headArgs[0],dependentArgs[1]])
        equalSet.add([becauseDependentArgs[0],dependentArgs[2]])
    return equalSet
        
#def handleWhileWords(props,rels):
#    equalArgSets=[]
#    for rel in rels:
#        (relName,dependentId,headId)=rel
#        if relName!="ADV": continue
#        (headId,headWord,headLemma,headPOS,headArgs)=findProp(props,headId)
#        dependentProp=findProp(props,dependentId)
#        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
#        if dependentLemma not in whileList:continue
#        
#        whileDependentId=getDependentId(rels,dependentId,"NCL")
#        (whileDependentId,whileDependentWord,whileDependentLemma,whileDependentPOS,whileDependentArgs)=findProp(props,whileDependentId)
#        
#        prdDependentId=getDependentId(rels,whileDependentId,"PRD")
#        (prdDependentId,prdDependentWord,prdDependentLemma,prdDependentPOS,prdDependentArgs)=findProp(props,prdDependentId)
#        
#        equalArgSets+=set([headArgs[0],dependentArgs[1]])
#        equalArgSets+=set([prdDependentArgs[0],dependentArgs[2]])
#    return equalArgSets
                  
            
    
                
def createNewPropsForNounConjs(props,rels,nounConjArgSets):
    global eventualityArgCounter
    eventualityArgCounter+=1
    newProps=[]
    newModifiers=[]
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
#                    newPropId=propIdCounter+1
                    newProp=(originalPropId,Word,Lemma,POS,newArgs) # Use original propId
                    newModifiers+=addModifiers(props,rels,originalProp,newProp)
                    newProps+=[newProp]
                    eventualityArgCounter+=1
#                    propIdCounter+=1
    return props+newProps+newModifiers

def createNewPropsForLightVerbs(props,rels):
    global eventualityArgCounter
    newProps=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName in ["NVE","ENC"]:
            eventualityArgCounter+=1
            
            dependentProp=findProp(props,dependentId)
            (dependentPropId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
            
            headProp=findProp(props,headId)
            (headId,headWord,headLemma,headPOS,headArgs)=headProp
            
            newProp=(-1,"",relName,"",["e%s"%eventualityArgCounter,dependentArgs[1],headArgs[0]])
            newProps+=[newProp]
            
    return props+newProps

def createNewPropsForNounsAndPossesives(props,rels):
    global eventualityArgCounter
    newProps=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName in ["MOZ"]:
            eventualityArgCounter+=1
            
            dependentProp=findProp(props,dependentId)
            (dependentPropId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=dependentProp
            
            headProp=findProp(props,headId)
            (headId,headWord,headLemma,headPOS,headArgs)=headProp
            
            if dependentLemma in pronouns:
                newProp=(-1,"","of-in","",["e%s"%eventualityArgCounter,dependentArgs[1],headArgs[1]])
            
            else:
                newProp=(-1,"","nn","",["e%s"%eventualityArgCounter,headArgs[1],dependentArgs[1]])
            
            newProps+=[newProp]
            
    return props+newProps
                
def createNewPropsForNounsWithPossesivePostfixes(props,rels):
    global eventualityArgCounter
    global entityArgCounter
    newProps=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop 
        if POS!=POSDict["N"]: continue
        postFix=word.replace(lemma, "") # if lemma==word, then postfix would be ""
        if postFix not in pronouns:
            continue 
        eventualityArgCounter+=1
        entityArgCounter+=1
        pronounArg="x%s"%str(entityArgCounter)
        #newProps+=[(id,postFix,getTranslit(postFix),POSDict["PR"],["e%s"%str(eventualityArgCounter),pronounArg])]
        newProps+=[(id,postFix,postFix,POSDict["PR"],["e%s"%str(eventualityArgCounter),pronounArg])]
        
        eventualityArgCounter+=1
        
        newProps+=[(-1,"","of-in","",["e%s"%eventualityArgCounter,args[1],pronounArg])]
        
    return props+newProps
def createNewPropsForPlural(props,rels):
    global eventualityArgCounter
    global entityArgCounter
    newProps=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        if POS!=POSDict["N"]:
            continue
        postFix=word.replace(lemma, "")
        if postFix not in pluralPostfixes:
            continue
        eventualityArgCounter+=1
        entityArgCounter+=1
        
        newProp=(-1,"","typelt","",["e%s"%eventualityArgCounter,args[1],"s%s"%entityArgCounter])
        
        newProps+=[newProp]
    return props+newProps

def createNewPropsForNegation(props,rels):
    global eventualityArgCounter
    global entityArgCounter
    newProps=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        
        if POS!=POSDict["V"]:
            continue
        
        prefix=word[0]
        if word[0] in negationList and lemma[0]!=word[0]:
        
            eventualityArgCounter+=1
            entityArgCounter+=1
            
            newProp=(-1,"","not","",["e%s"%eventualityArgCounter,args[0]])
            
            newProps+=[newProp]
    return props+newProps


def createNewPropsForPronouns(props,rels):
    global eventualityArgCounter
    global entityArgCounter
    newProps=[]
    for prop in props:
        
        (id,word,lemma,POS,args)=prop
        if POS!=POSDict["PR"]:
            continue
        if lemma not in pronouns:
            continue
        (person,animate)=pronouns[lemma]
        if person=="2":
            eventualityArgCounter+=1
            entityArgCounter+=1
            newProp=(-1,"","typelt","",["e%s"%eventualityArgCounter,args[1],"s%s"%entityArgCounter])
            newProps+=[newProp]
            
        eventualityArgCounter+=1
        entityArgCounter+=1
        if animate=="1":
            newProp=(-1,"","person","",["e%s"%eventualityArgCounter,args[1]])
            newProps+=[newProp]
        if animate=="0":
            newProp=(-1,"","thing","",["e%s"%eventualityArgCounter,args[1]])
            newProps+=[newProp]
    return props+newProps

    
def createNewPropsForConditionals(props,rels):
    global eventualityArgCounter
    newProps=[]
    relsToRemove=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName in ["AJUCL"]:
            eventualityArgCounter+=1
            
            headProp=findProp(props,headId)
            (headId,headWord,headLemma,headPOS,headArgs)=headProp
            
            ifProp=findProp(props,dependentId) #if
            (ifPropId,ifWord,ifLemma,ifPOS,ifArgs)=ifProp
            if ifLemma not in conditionalList:continue
            ifVerbId=getDependentId(rels,ifPropId,"PRD")
            (ifVerbId,ifVerbWord,ifVerbLemma,ifVerbPOS,ifVerbArgs)=findProp(props,ifVerbId)
            if len(ifVerbArgs)<4:
                relsToRemove+=[rel]
                continue
            newProp=(-1,"","imp","",["e%s"%eventualityArgCounter,headArgs[0],ifVerbArgs[0]])
            
            newProps+=[newProp]
    newRels=[]
    for rel in rels:
        if rel not in relsToRemove:
            newRels+=[rel]
            
    return (newRels,props+newProps)
 
def handleVConj(props,rels):
    #if one of the verbs has no subject, make their subject the same.
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName =="VCONJ":
            
            conj1Prop=findProp(props,headId)
            conj2Id=getDependentId(rels,dependentId,"PREDEP")
            if conj2Id==None:
                continue
            conj2Prop=findProp(props,conj2Id)
            (conj1Id,conj1Word,conj1Lemma,conj1POS,conj1Args)=conj1Prop
            (conj2Id,conj2Word,conj2Lemma,conj2POS,conj2Args)=conj2Prop
            conj1Arg=conj1Args[1]
            conj2Arg=conj2Args[1]
            
            if "u" in conj1Arg and "x" in conj2Arg: 
                conj1Args[1]=conj2Arg

            if "x" in conj1Arg and "u" in conj2Arg:
                conj2Args[1]=conj1Arg[1]
    return props

def handleVCL(props,rels):
    global eventualityArgCounter
    equalArgSets=[]
#    newProp=None
    relsToRemove=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName !="VCL":continue
            
        verb1Prop=findProp(props,headId)
        (verb1Id,verb1Word,verb1Lemma,verb1POS,verb1Args)=verb1Prop
        if len(verb1Args)<4:
            relsToRemove+=[rel]
            continue
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=findProp(props,dependentId) #keh
        verb2Id=getDependentId(rels,dependentId,"PRD")
        if verb2Id==None:
            verb2Id=dependentId
            
#            eventualityArgCounter+=1
#            propIdCounter+=1
#            newProp=(propIdCounter,"","VCL","",["e%s"%eventualityArgCounter,verb1Args[0],verb2Args[0]])
            
        else:
            equalArgSets+=[set([dependentArgs[1],verb1Args[0]])]
        
        (verb2Id,verb2Word,verb2Lemma,verb2POS,verb2Args)=findProp(props,verb2Id)
        if len(verb2Args)<4:
            relsToRemove+=[rel]
            continue
        equalArgSets+=[set([verb1Args[2],verb2Args[0]])]
    
    newRels=[]
    for rel in rels:
        if rel not in relsToRemove:
            newRels+=[rel]
    return (newRels,equalArgSets)

def handleAJUCL(props,rels): # although because words and conditional words are also identified with AJUCL, they are handled separately. This is for the cases like: in kaar ra bekonid <ta> rastegaar shavid. And we want to plug in the right arguments for <ta>
    equalArgSets=[]
#    newProp=None
    relsToRemove=[]
    for rel in rels:
        (relName,dependentId,headId)=rel
        if relName !="AJUCL":continue
            
        verb1Prop=findProp(props,headId)
        (verb1Id,verb1Word,verb1Lemma,verb1POS,verb1Args)=verb1Prop
        if len(verb1Args)<4:
            relsToRemove+=[rel]
            continue
        (dependentId,dependentWord,dependentLemma,dependentPOS,dependentArgs)=findProp(props,dependentId) #keh, ta
        verb2Id=getDependentId(rels,dependentId,"PRD")
        if verb2Id!=None:
            (verb2Id,verb2Word,verb2Lemma,verb2POS,verb2Args)=findProp(props,verb2Id)
            if len(verb2Args)<4:
                relsToRemove+=[rel]
                continue
            equalArgSets+=[set([dependentArgs[1],verb1Args[0]])]
            equalArgSets+=[set([dependentArgs[2],verb2Args[0]])]
    newRels=[]
    for rel in rels:
        if rel not in relsToRemove:
            newRels+=[rel]
    return (newRels,equalArgSets)
        
        
    
            
def refineRels(props,rels):
    newRels=[]
    
    propIds=[]
    for (id,word,lemma,POS,args) in props:
        propIds+=[id]
    for rel in rels:
        (relName,id,dep)=rel
        if id in propIds and dep in propIds:
            newRels+=[rel]
    return newRels    

def removeAllNonAlphaNum(word):
    for char in listOfNonAlphaNumChars:
        word=word.replace(char,"")
    return word.strip()
    
    
    
def hasAlphabet(word):
    if word.strip()=="_": return 0
    modifiedWord=removeAllNonAlphaNum(word)
    if modifiedWord=="":return 0
    #if re.match("\w+", word):
    #    return 1        
    return 1
def refineProps(props):
    newProps=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        if POS not in POSStopList and hasAlphabet(lemma):
            newProps+=[prop]
            
    return newProps    
def createLF(tokens,sentenceId):
    props=[]
    rels=[]
    words=[]
    for token in tokens:
        (id,word,lemma,POS,relName,dep)=token
        words+=[word]
        
        #props+=[(id,word,getTranslit(lemma),POS,getArgs(POS))]
        #print "(word,lemma): %s,%s"%(word,lemma)
        props+=[(id,word,lemma,POS,getArgs(POS))]
        rels+=[(relName,id,dep)]
    sentence= " ".join(words)
    props=refineProps(props)
    
    rels=refineRels(props,rels)
    LF=(sentenceId,sentence,props,rels)
    LF2=resolveArgs(LF)
    return LF2

def getSentenceAndLFString(lf):
    (sentenceId,sentence,props,rels)=lf
    words=[]
    PropStrings=[]
    for prop in props:
        (id,word,lemma,POS,args)=prop
        words+=[word]
        pstr=propToString(sentenceId,prop)
        PropStrings+=[pstr]
    lfLine=" & ".join(PropStrings)
    
    return (sentence,sentenceId,lfLine)

def addToEqualArgSet(equalArgSets,newEqualArgSets):
    for argSet in newEqualArgSets:
        found=0
        for equalArgSet in equalArgSets:
            if equalArgSet.intersection(argSet):
                equalArgSet.update(argSet)
                found=1
        if not found:
            equalArgSets+=[argSet]
            
def resolveArgs(LF):
    (sentenceId,sentence,props,rels)=LF
    
    
    props=createNewPropsForLightVerbs(props,rels)
#    print "1%s"%props
    props=createNewPropsForNounsWithPossesivePostfixes(props,rels)
#    print "2%s"%props
    props=createNewPropsForNounsAndPossesives(props,rels)
#    print "3%s"%props
    props=createNewPropsForPlural(props,rels)
#    print "4%s"%props
    props=createNewPropsForPronouns(props,rels)
#    print "5%s"%props
    (newRels,props)=createNewPropsForConditionals(props,rels)
#    print "6%s"%props
    rels=newRels
    props=createNewPropsForNegation(props,rels)
#    print "7%s"%props
    
    propDict=createPropDict(props)
    equalArgSets=getEqualArgSets(propDict,rels)  
    addToEqualArgSet(equalArgSets,handleBecauseWords(props,rels))
    (newRels,additionalEqualArgSets)=handleVCL(props,rels)
    addToEqualArgSet(equalArgSets,additionalEqualArgSets)
    rels=newRels
    (newRels,additionalEqualArgSets)=handleAJUCL(props,rels)
    addToEqualArgSet(equalArgSets,additionalEqualArgSets)
    rels=newRels
    
    
    #addToEqualArgSet(equalArgSets,handleWhileWords(props,rels))  because words are nouns and are adverbs in farsi.
    props=replaceEqualArgs(props,equalArgSets)
#    print "8%s"%props
    
    props=handleVConj(props,rels)
#    print "9%s"%props
    nounConjArgSets=getNounConjArgSets(props,rels)
    props=createNewPropsForNounConjs(props,rels,nounConjArgSets)
#    print "10%s"%props
           
    return (sentenceId,sentence,props,rels)               

unknownargCounter=0
entityArgCounter=0
eventualityArgCounter=0

loadFarsiWordsForLFFile(farsiWordsForLFFile)


paragraphId="NILOO"
sentenceId=1
tokens=[]

paragraph=""
paragraphLFString=""

line=inputFile.readline()

while line!="":
    
    line=line.replace(u'\u200e',"")
    if line.strip()=="" and len(tokens)!=0: #one sentence read, process it 
        lf=createLF(tokens,sentenceId) #create logical form
        (sentence,sentenceId,LFString)=getSentenceAndLFString(lf) # get sentence and string representation of the logical form
        
        
        if "META" in sentence: #this was not a real sentence, it was just a marker for a new paragraph -> get the paragraph id , reset everything and don't print anything in the output file 
            if paragraphId != "NILOO":
                
                paragraphString="% " + "%s\nid(%s).\n%s\n"%(paragraph,str(paragraphId),paragraphLFString[3:])
                paragraphString=paragraphString.encode('utf-8')
                outputFile.write(paragraphString)
    #        sys.stdout.write(lfToString(lf).encode("utf-8"))
            
            #get new paragraph id and reset everything
            paragraphId=sentence.replace("<META>","").replace("%","").replace(".","").strip()
            paragraph=""
            paragraphLF=""
            paragraphString=""
            paragraphLFString=""
            tokens=[] 
            unknownargCounter=0 
            entityArgCounter=0
            eventualityArgCounter=0
            
            line=inputFile.readline()
            continue
        
           
        if paragraphId=="NILOO": # still no <META> found: the sentence and LF are printed and all arg counters are reset
            sentenceString="% "+"%s\nid(%s).\n%s\n"%(sentence,str(sentenceId),LFString)
            sentenceString=sentenceString.encode('utf-8')
            outputFile.write(sentenceString)
    #        sys.stdout.write(lfToString(lf).encode("utf-8"))
            unknownargCounter=0 
            entityArgCounter=0
            eventualityArgCounter=0
        else:
            paragraph+=sentence
            paragraphLFString="%s & %s"%(paragraphLFString,LFString)
            
        sentenceId+=1
        tokens=[] # in any case, token list should be emptied for the next sentence.
                
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

if len(tokens)!=0:
    lf=createLF(tokens,sentenceId) #create logical form
    (sentence,sentenceId,LFString)=getSentenceAndLFString(lf) # get sentence and string representation of the logical form

    if paragraphId=="NILOO":
        sentenceString="% "+"%s\nid(%s).\n%s\n"%(sentence,str(sentenceId),LFString)
        sentenceString=sentenceString.encode('utf-8')
        outputFile.write(sentenceString)
        
    else:
        paragraph+=sentence
        paragraphLFString="%s & %s"%(paragraphLFString,LFString)
        paragraphString="% "+"%s\nid(%s).\n%s\n"%(paragraph,str(paragraphId),paragraphLFString[3:])
        paragraphString=paragraphString.encode('utf-8')
        outputFile.write(paragraphString)

if paragraphId!="NILOO":  
    paragraphString="% " + "%s\nid(%s).\n%s\n"%(paragraph,str(paragraphId),paragraphLFString[3:])
    paragraphString=paragraphString.encode('utf-8')
    outputFile.write(paragraphString)                  

inputFile.close()
outputFile.close()

