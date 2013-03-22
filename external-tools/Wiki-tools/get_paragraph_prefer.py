#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import codecs
import psycopg2.extras

def searchDB(CONN_STRING,query,myset):
    rows = None
    try:
        if myset.debug:
            print '==> ',query

        con = psycopg2.connect(CONN_STRING) 
        con.set_client_encoding('UTF8')
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        #get result
        rows = cur.fetchall()
        if myset.debug:
            print '==> ',str(len(rows))
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()
    return rows
    

def query_change(query,inword,myset):
    if not myset.substring and myset.case_sensitive: #exact
        query = query.replace('ilike','=')
    if myset.case_sensitive:
        query = query.replace('ilike','like')
    query = query.replace('@@@inword@@@',inword)
    return query
        
def searchWiki(CONN_STRING,titles,table_name):
    k=0
    try:
        con = psycopg2.connect(CONN_STRING) 
        con.set_client_encoding('UTF8')
        
        for i in range(0,len(titles)):
            title = titles[i]
            query = "select title,abstract from TABLE_NAME where title = '@@@inword@@@'"
            query = query.replace('TABLE_NAME',table_name)
            query = query.replace('@@@inword@@@',title)
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query)
            #get result
            rows = cur.fetchall()
            for row in rows:
                k+=1
                print '#'+str(k)+" TITLE: "+row['title']
                print '#'+str(k)+" ABSTRACT: "+row['abstract']
                
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()
        
# get the prefered wiki for certain name; return the wiki_titles
def prefer_search_word(myset,word):
    # English
    titles = []
    if myset.lang == 'EN':        
        # Approach #1: "__"@eng =='<isPreferredMeaningOf>'==> <Yago> =='<hasWikipediaUrl>'==> <URL>
        if myset.debug:
            print '==> Apro#1'
        query = "select y2.object from yagofacts y1, yagofacts y2 where y1.object = '@@@inword@@@' and y1.predicate = '<isPreferredMeaningOf>' and y1.subject = y2.subject and y2.predicate = '<hasWikipediaUrl>' limit 1"
        query = query.replace('@@@inword@@@',word)
        rows=searchDB(myset.CONN_STRING,query,myset)
        if len(rows)>0: # found
            wikiUrl = rows[0]['object']
            title = wikiUrl.split('wikipedia.org/wiki/')[-1][:-1]
            titles.append(title)
            searchWiki(myset.CONN_STRING,titles,myset.table_name)
            return titles

        # Approach #2:
        # #2.1 "__"@eng =='<isPreferredMeaningOf>'==> <wordnet> =='skos:prefLabel'==> "__"@eng =='ilike'==> title
        if myset.debug:
            print '==> Apro#2.1'
        titles = []
        query = "select distinct y2.object from yagofacts y1, yagofacts y2 where y1.object = '@@@inword@@@' and y1.predicate = '<isPreferredMeaningOf>' and y1.subject = y2.subject and y2.predicate = 'skos:prefLabel'"
        query = query.replace('@@@inword@@@',word)
        rows=searchDB(myset.CONN_STRING,query,myset)
        if len(rows)>0: #found
            title = rows[0]['object'][1:-5].replace(' ','_')
            query = "select title from wiki_en where title ilike '@@@inword@@@'"
            query = query.replace('@@@inword@@@',title)
            rows = searchDB(myset.CONN_STRING,query,myset)
            if len(rows)>0:
                for row in rows:
                    title = row['title']
                    titles.append(title)
                searchWiki(myset.CONN_STRING,titles,myset.table_name)
                return titles

        # #2.2 no result in 2.1 then search title in wiki_en directly.
        # if myset.debug:
        #     print '==> Apro#2.2'
        # query = "select title,abstract from TABLE_NAME where title ilike '@@@inword@@@'"
        # title = word[1:-5].replace(' ','_')
        # query = query.replace('@@@inword@@@',title)
        # query = query.replace('TABLE_NAME',myset.table_name)
        # rows = searchDB(myset.CONN_STRING,query,myset)
        # if len(rows)>0:
        #     for row in rows:
        #         title = row['title']
        #         titles.append(title)
        #     searchWiki(myset.CONN_STRING,titles,myset.table_name)
        #     return titles

        # #2.3 no result search other meanings (several)
        titles = []
        if myset.debug:
            print '==> Apro#2.3'
        query = "select distinct y2.object from yagofacts y1, yagofacts y2 where y1.object = '@@@inword@@@' and y1.predicate = '<isPreferredMeaningOf>' and y1.subject = y2.subject and y2.predicate = 'rdfs:label'"
        query = query.replace('@@@inword@@@',word)
        rows = searchDB(myset.CONN_STRING,query,myset)
        if len(rows) > 0: #found
            literals=[]
            for row in rows:
                literal = row['object'][1:-5].replace(' ','_')
                literals.append(literal)
            titleset={}
            for literal in literals:
                query = "select title from TABLE_NAME where title ilike '@@@inword@@@'"
                query = query.replace('@@@inword@@@',literal)
                rows = searchDB(myset.CONN_STRING,query,myset)
                for row in rows:
                    titie = row['title']
                    titleset[title]=1
            for title in titleset:
                titles.append(title)
            searchWiki(myset.CONN_STRING,titles,myset.table_name)
            return titles
    # Others
    else:
        titles=[]
        # #2.2 no result in 2.1 then search title in wiki_en directly.
        # if myset.debug:
        #     print '==> Apro#2.2'
        
        # query = "select title,abstract from TABLE_NAME where title ilike '@@@inword@@@'"
        # title = word[1:-5].replace(' ','_')
        # query = query.replace('@@@inword@@@',title)
        # query = query.replace('TABLE_NAME',myset.table_name)
        # rows = searchDB(myset.CONN_STRING,query,myset)
        # if len(rows)>0:
        #     for row in rows:
        #         title = row['title']
        #         titles.append(title)
        #     print titles
        #     searchWiki(myset.CONN_STRING,titles,myset.table_name)
        #     return titles

        # #2.2 IF direct search the titles and no results. '__'@other --> <wordnet> -'skos:prefLabel'-> '__'@eng --> <Wiki> -> Eng
        if myset.debug: 
            print '==> Apro#2.2'
        query = "select y2.object from yagofacts y1, yagofacts y2 where y1.object = '@@@inword@@@' and y1.predicate = 'rdfs:label' and y1.subject = y2.subject and y2.predicate = 'skos:prefLabel'; "
        query = query.replace('@@@inword@@@',word)
        rows = searchDB(myset.CONN_STRING,query,myset)
        if len(rows)>0:
            literals = []
            for row in rows:
                literal = row['object'][1:-5].replace(' ','_')
                literals.append(literal)
            titleset = {}
            engTitles=[]
            for literal in litreals:
                query = "select title from wiki_en where title ilike '@@@inword@@@'"
                query = query.replace('@@@inword@@@',literal)
                rows = searchDB(myset.CONN_STRING,query,myset)
                for row in rows:
                    titie = row['title']
                    titleset[title]=1
            for title in titleset:
                engTitles.append(title)
            titleset = {}
            for engTitle in engTitles:
                query = "select otherTitle from multilink where engTitle = '__engTitle__' and lang = '__lang__'"
                query = query.replace('__engTitle__',engTitle)
                query = query.replace('__lang__',myset.lang)
                rows = searchDB(myset.CONN_STRING,query,myset)
                for row in rows:
                    titleset[row['otherTitle']] = 1
            titles=[]
            for title in titleset:
                titles.append(title)
            searchWiki(myset.CONN_STRING,titles,myset.table_name)
            return titles

        # #2.3 no result search other meanings (several)
        if myset.debug:
            print '==> Apro#2.3'
        query = "select distinct y2.object from yagofacts y1, yagofacts y2 where y1.object = '@@@inword@@@' and y1.predicate = 'rdfs:label' and y1.object != y2.object and y2.object like '%__lang__' and y1.subject = y2.subject and y2.predicate = 'rdfs:label'"
        query = query.replace('@@@inword@@@',word)
        query = query.replace('__lang__',myset.qlang)
        rows = searchDB(myset.CONN_STRING,query,myset)
        if len(rows) > 0: #found

            literals=[]
            for row in rows:
                literal = row['object'][1:-5].replace(' ','_')
                literals.append(literal)
            titleset={}
            for literal in literals:
                query = "select title from TABLE_NAME where title ilike '@@@inword@@@'"
                query = query.replace('@@@inword@@@',literal)
                rows = searchDB(myset.CONN_STRING,query,myset)
                for row in rows:
                    titie = row['title']
                    titleset[title]=1
            for title in titleset:
                titles.append(title)
            searchWiki(myset.CONN_STRING,titles,myset.table_name)
            return titles
    return titles

def prefer_search(myset):
    # prepare for the query word
    inword_yago = ''
    inword_wiki = ''
    if myset.substring:
        inword_yago = '"%'+myset.inword+'%"'+ myset.qlang
        inword_wiki = '%'+myset.inword.replace(' ','_')+'%'
    else:
        inword_yago = '"'+myset.inword+'"'+myset.qlang
        inword_wiki = myset.inword.replace(' ','_')

    # prepare the result both in Yago and Wiki
    
    
    wikiNames = {}
    query = "select distinct title from TABLE_NAME where title ilike '@@@inword@@@'"
    query = query.replace('TABLE_NAME',myset.table_name)
    query = query_change(query,inword_wiki,myset)
    rows = searchDB(myset.CONN_STRING,query,myset)
    for row in rows:
        title = row['title']
        wikiNames[title]=1

    i = 0
    
    for title in wikiNames:
        if wikiNames[title] == 1:
            i=i+1
            print 'Word #'+str(i)+': '+title
            titles=[]
            titles.append(title)
            searchWiki(myset.CONN_STRING,titles,myset.table_name)
    
    if len(rows)>0:
        return 0;

    yagoNames = []
    query = "select distinct object from yagofacts where object ilike '@@@inword@@@'"
    query = query_change(query,inword_yago,myset)
    rows = searchDB(myset.CONN_STRING,query,myset)
    for row in rows:
        literal = row['object']
        yagoNames.append(literal)

    for litreal in yagoNames:
        titles=prefer_search_word(myset,literal)
        if len(titles)==0:
            continue
        i=i+1
        print 'Word #'+str(i)+': '+literal
        for title in titles:
            if title in wikiNames:
                wikiNames[title]=0

    
    
    return 0
