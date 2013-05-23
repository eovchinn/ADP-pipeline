#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import psycopg2
import urllib
import global_setting
import os
import subprocess
import parse
# function to insert records

def insert_records(con,records,table_name):
    try:
        query = "INSERT INTO "+table_name+" (id, lang, title, wiki_url,abstract,parse_result)  VALUES( %s, %s, %s, %s, %s, %s)"
        # query = "INSERT INTO "+table_name+" (id, lang, title, wiki_url,abstract)  select %s, %s, %s, %s, %s where not exists (select id from "+table_name+" where id = %s)"
        cur=con.cursor()
        cur.executemany(query,records)
        con.commit()
    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
        print 'Error %s' % e
        sys.exit(-1)

# function to create the table

def create_table(table_name):
    # CONN_STRING: you need to change it 
    CONN_STRING= global_setting.get_CONN()

    try:

        con = psycopg2.connect(CONN_STRING)
        con.set_client_encoding('UTF8')

        #check wheter table exsits

        query = "select * from information_schema.tables where table_name='"+table_name+"'"
        cur = con.cursor()
        cur.execute(query)
        rows=cur.fetchall()

        if len(rows) == 0 : #table doesn't exist
            cur = con.cursor()
            query='create table '+table_name+'(id char(12) PRIMARY KEY,lang char(2),title text,wiki_url text, abstract text, parse_result text)'
            cur.execute(query)
            con.commit()
        
        return con
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)

def main():

    from optparse import OptionParser
   
    # option
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f","--file", dest='filePath',help="file path")
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    parser.add_option("-s","--startline",dest='startline',help="start line number [n]. This means the first n lines of the file will not be processed!")
    parser.add_option("-x",'--suffixID',dest='suffixID',help="the ID suffix: E(have relavant English pages, N(no relevant english pages.")
    parser.add_option("--common",dest='commonDir',help='the NLPipeline_MULT_stdinout.py folder path')
    parser.add_option("--temp",dest = 'tempFile',help='the temp File path')
    parser.set_defaults(startline='1')
    parser.set_defaults(suffixID='')
    (options,args) = parser.parse_args()
    
    if not options.filePath:
        parser.error("Please input the file path")
    if not options.lang:
        parser.error("Please specify the languages:EN,ES,RU,FA")
    
    try:
        int(options.startline)
    except ValueError, e:
        parser.error("Please input a number for -s")
        
    filePath=options.filePath
    lang=options.lang
    startline=int(options.startline)
    suffixID=options.suffixID
    
    indexs={"EN":0,"ES":1,"RU":2,"FA":3}
    urlpres=["http://en.wikipedia.org/wiki/","http://es.wikipedia.org/wiki/","http://ru.wikipedia.org/wiki/","http://fa.wikipedia.org/wiki/"]
    table_names=["wiki_en","wiki_es","wiki_ru","wiki_fa"]
    
    index=indexs[lang]
    urlpre=urlpres[index]
    table_name=table_names[index]
    
    commonDir = options.commonDir
    tempFile = options.tempFile


    #Database setting and create table

    con = create_table(table_name)
    
    #process the data

    file=open(filePath,'r')
    i,j,nr = -1, 0, 1000
    records=[]
    while True:
        line=file.readline()
        if not line or i==2:
            insert_records(con,records,table_name)
            records=[]
            break
        else:
            i+=1
        j+=1
        if j<=startline:
            continue

        #decode
        line=line.decode('raw_unicode_escape')
        line=line[:-3]
        ll=line.split(" ",2)
        
        #for title
        title = ll[0].split("dbpedia.org/resource/")[-1][:-1]
        title = urllib.unquote(title)
        #for url
        url=urlpre+title
        #for abstraction
        abstract=ll[-1]
        result = parse.parse(abstract,commonDir,tempFile,lang,False)
        abstract = result[0]
        parse_result = result[1]
        #for id
        ID=lang+suffixID+str(i)
        record=(ID,lang,title,url,abstract,parse_result)
        # print title
        # print url
        # print abstract
        # print '\n'
        records.append(record)
        # when there are 1000 records:
        if len(records) >= nr:
            insert_records(con,records,table_name)
            records=[]

        if i % 10000 == 0:
            print "%d entries inserted." % i

    if con:
        con.close()

    # end of main()

if __name__ == "__main__":
    main()

    
