import codecs
import sys
import os

inputFolder=sys.argv[1]
sourceAxiomFile=codecs.open(sys.argv[2], encoding='utf-8')
targetAxiomFile=codecs.open(sys.argv[3], encoding='utf-8')
outputFile=sys.stdout

var_name_values={"source":"","target":"","sourceConceptSubDomain":"","sourceFrame":"","targetConceptDomain":"","targetConceptSubDomain":"","targetFrame":""}

listOfJsonFiles=os.listdir(inputFolder)
for jsonFileName in listOfJsonFiles:
    absFilePath="%s/%s"%(inputFolder, jsonFileName)
    jsonFile=codecs.open(absFilePath, encoding='utf-8')
    lines=jsonFile.readlines()
    isFirstSourceNode=True
    for varName in var_name_values:
        for line in lines:
            if varName in line: 
                if varName=="source" and not isFirstSourceNode: continue
                var_name_values[varName]=getValue(line)
                if varName=="source":isFirstSourceNode=False
    jsonFile.close()
    
#now we have read all the name_values
#read the axiom files and compare against the name_values

sourceAxLines=sourceAxiomFile.readlines()
targetAxLines=targetAxiomFile.readlines()   



sourceAxiomFile.close()
targetAxiomFile.close()
    