#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import psycopg2
import urllib
import mydb

def processFile(con,query,file,isType):
    i = 0
    records=[]
    file.readline() # skip the first line.
    while True:
        line = file.readline()
        if not line:
            if len(records)>0:
                mydb.executeQueryRecords(con,query,records,False)
                records=[]
            break
        line=line.decode('raw_unicode_escape')
        ll = line.split(' ')
        record = None
        if isType:
            record=(ll[0],ll[2])
        else:
            record = (ll[0],ll[1],ll[2])
        records.append(record)
        i+=1
        if i%10000 == 0:
            print '%d records inserted!' % i
        if len(records)>100:
            mydb.executeQueryRecords(con,query,records,False)
            records=[]

def main():

    from optparse import OptionParser
   
    # option
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--tfile", dest='type_filePath',help="Type file path")
    parser.add_option("-p","--pfile", dest='property_filePath',help="Property file path")
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    parser.add_option("-d","--debug",dest = "debug" , action = "store_true",
                  help="output debug info, default is false", default = False)
   
    (options,args) = parser.parse_args()
    
    lang = options.lang
    tfilePath = options.type_filePath
    pfilePath = options.property_filePath
    debug = options.debug
    
    indexs={"EN":0,"ES":1,"RU":2,"FA":3}
    type_table_names=["type_en","type_es","type_ru","type_fa"]
    property_table_names=["property_en","property_es","property_ru","property_fa"]
    
    index=indexs[lang]
    type_table_name = type_table_names[index]
    property_table_name = property_table_names[index]

    CONN_STRING=mydb.get_CONN()
    con = mydb.getCon(CONN_STRING)
    # create table
    
    querys=[]
    querys.append( 'DROP TABLE IF EXISTS '+type_table_name+';' )
    querys.append('DROP TABLE IF EXISTS '+property_table_name+';')
    querys.append('CREATE TABLE '+type_table_name+'(entity varchar,type varchar);')
    querys.append('CREATE TABLE '+property_table_name+'(entity varchar,property varchar,value varchar);')
    mydb.executeManyQuery(con,querys,debug)
      
    # process the data
    tfile = open(tfilePath,'r')
    pfile = open(pfilePath,'r')
    # for the type file
    query_t='insert into __table_name__(entity,type) VALUES(%s, %s)'
    query_t=query_t.replace('__table_name__',type_table_name)
    processFile(con,query_t,tfile,True)
    # for property table
    query_p='insert into __table_name__(entity,property,value) VALUES(%s, %s, %s)'
    query_p=query_p.replace('__table_name__',property_table_name)
    processFile(con,query_p,pfile,False)
    
    # build index
    querys=[]
    query = 'create index __indexName__ on __index__;'
    querys.append(query.replace('__indexName__',type_table_name+'_entity').replace('__index__',type_table_name+'(entity)'))
    querys.append(query.replace('__indexName__',type_table_name+'_type').replace('__index__',type_table_name+'(type)'))
    querys.append(query.replace('__indexName__',property_table_name+'_entity').replace('__index__',property_table_name+'(entity)'))
    querys.append(query.replace('__indexName__',property_table_name+'_property').replace('__index__',property_table_name+'(property)'))
    mydb.executeManyQuery(con,querys,debug)
      
    # close db
    mydb.closeCon(con)
    
if __name__ == '__main__':
    main()
  
