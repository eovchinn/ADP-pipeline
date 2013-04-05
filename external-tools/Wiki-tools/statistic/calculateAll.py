#!/usr/bin/python
# -*- coding: utf-8 -*-

import mydb
import xml.etree.cElementTree as xml
import calculate


from optparse import OptionParser
    #option
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-l","--lang", dest="lang",help="language:EN,RU,ES")
(options,args) = parser.parse_args()

lang = options.lang
slangs = {'EN':'en',"ES":'es',"RU":'ru',"FA":'fa'}
slang = slangs[lang]

# some namespace
rdf = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
owl = '{http://www.w3.org/2002/07/owl#}'
rdfs = '{http://www.w3.org/2000/01/rdf-schema#}'
xml_ns = '{http://www.w3.org/XML/1998/namespace}'

def findLabel(tree,name,lang,isType):
    tagName = owl+'Class'
    if isType == 1:
        tagName = owl+'ObjectProperty'
    elif isType == 2:
        tagName = owl+'DatatypeProperty'
    
    attribName = rdf + 'about'
    langName = rdfs + 'label'
    langAttr = xml_ns+'lang'
    xpath = ".//__tagName__[@__attribName__='__classname__']/__langName__[@__langAttr__='__lang__']"
    xpath = xpath.replace('__tagName__',tagName)
    xpath = xpath.replace('__attribName__',attribName)
    xpath = xpath.replace('__classname__',name)
    xpath = xpath.replace('__langName__',langName)
    xpath = xpath.replace('__langAttr__',langAttr)
    xpath = xpath.replace('__lang__',lang)
    # xpath = ".//__tagName__"
    #xpath = xpath.replace('__tagName__',tagName)
    #print xpath
    nodes = tree.findall(xpath)
    if len(nodes) == 0:
        return None
    else :
        return nodes[0].text

originPath = 'dbpedia_3.8.xml'
originTree = xml.parse(originPath)

#findLabel(originTree,'http://dbpedia.org/ontology/soocerLeagueRelegated','en',1)

# create table 
CONN_STRING = mydb.get_CONN()
con = mydb.getCon(CONN_STRING)
tableNames={'EN':'statistic_en','RU':'statistic_ru','ES':'statistic_es',"FA":'statistic_fa'}
tableName = tableNames[lang]
query = 'DROP TABLE IF EXISTS '+ tableName+';'
mydb.executeQuery(con,query,True)
query = 'CREATE TABLE __tableName__(type varchar, property varchar, native_type varchar, native_property varchar, hit int, total int);'
query = query.replace('__tableName__',tableName)
mydb.executeQuery(con,query,True)

records=[]
insertQuery='insert into __table_name__(type,property,native_type,native_property,hit,total) VALUES(%s,%s,%s,%s,%s,%s);'
insertQuery = insertQuery.replace('__table_name__',tableName)
if lang !="FA":
    #print insertQuery
    filepath = 't.xml'
    tree = xml.parse(filepath)
    xmlRoot = tree.getroot()
    for c in xmlRoot.findall('.//Type'):
        typeName = c.attrib['name']
        #typeName = 'http://dbpedia.org/ontology/University'
        native_type = findLabel(originTree,typeName,slang,0)
        if native_type == None:
            native_type = 'None'
        properties = calculate.calculate(typeName,lang)
        #print properties
        total = properties['__total__']
        for property in properties:
            native_property = ''
            if property == '__total__':
                native_property = '__total__'
            else:
                native_property = findLabel(originTree,property[1:-1],slang,1)
                if native_property == None:
                    native_property = findLabel(originTree,property[1:-1],slang,2)
                if native_property == None:
                    native_property = 'None'

            hit = properties[property]
            record = (typeName,property,native_type,native_property,hit,total)
            records.append(record)
            if len(records)>100:
                mydb.executeQueryRecords(con,insertQuery,records,False)
                records=[]
        #break
    if len(records)>0:
        mydb.executeQueryRecords(con,insertQuery,records,False)
        records=[]
else: # lang == 'FA'
    typeFile = open('types_fa.txt','r')
    while True:
        line = typeFile.readline()
        if not line:
            break
        typeName = line.strip()
        properties = calculate.calculate(typeName,lang)
        total = properties['__total__']
        for property in properties:
            native_property = ''
            if property == '__total__':
                native_property = '__total__'
            else:
                native_property = 'None'
            native_type = 'None'
            hit = properties[property]
            record = (typeName,property,native_type,native_property,hit,total)
            records.append(record)
            if len(records)>100:
                mydb.executeQueryRecords(con,insertQuery,records,False)
                records=[]
        
    if len(records)>0:
        mydb.executeQueryRecords(con,insertQuery,records,False)
        records=[]
