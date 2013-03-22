#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import global_setting
import urllib
import psycopg2
import psycopg2.extras

def insert_records(con,records):
    try:
        query = "INSERT INTO multiLink(engTitle, lang, otherTitle) VALUES( %s, %s, %s)"
        cur=con.cursor()
        cur.executemany(query,records)
        con.commit()
    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
        print 'Error %s' % e
        sys.exit(-1)

def extractTitle(str):
    ss = str.split('dbpedia.org/resource/')[1][:-1]
    return ss

def main():
    from optparse import OptionParser
    
    #option
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d","--dir", dest="dirPath",help="the *.nt files dir path")
    (options,args) = parser.parse_args()
    
    if not options.dirPath:
        parser.error("Please input the dir path")
    
    dirPath=options.dirPath
    filePath = dirPath + '/' + 'interlanguage_links_same_as_en.nt'
    CONN_STRING = global_setting.get_CONN()

    # create table
    try:
        con = psycopg2.connect(CONN_STRING)
        con.set_client_encoding('UTF8')
        cur = con.cursor()

        query = 'DROP TABLE IF EXISTS multilink;'
        output = cur.execute(query)
        con.commit()
        
        print query
        query = 'CREATE TABLE multiLink(engTitle varchar,lang varchar, otherTitle varchar);'
        cur.execute(query)
        con.commit()
        
        print query
        #process files
        file = open(filePath, 'r' )
        file.readline()
        records = []
        i = 0
        while True:
            line = file.readline()
            if not line:
                if len(records) > 0:
                    insert_records(con,records)
                    records=[]
                break
            line = line.decode('raw_unicode_escape')
            ll = line.split(' ')
            lang = ''
            if ll[2].startswith('<http://es.dbpedia.org/resource'):
                lang = 'ES'
            if ll[2].startswith('<http://fa.dbpedia.org/resource'):
                lang = 'FA'
            if ll[2].startswith('<http://ru.dbpedia.org/resource'):
                lang = 'RU'
            if lang == '':
                continue
            i+=1
            engTitle = extractTitle(ll[0])
            otherTitle = extractTitle(ll[2])
            record = (engTitle, lang , otherTitle)
            records.append(record)
            if len(records) > 100:
                insert_records(con,records)
                records=[]
            if i%10000 == 0:
                print '%d records inserted!', i 
        print i
        
        con.commit()
        # buildIndex
        query = 'CREATE INDEX multilink_engTitle on multilink(engTitle);'
        cur.execute(query)
        con.commit()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)
    
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    main()
