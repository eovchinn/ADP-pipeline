#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import codecs
import psycopg2.extras


def main():
    # database settings
    CONN_STRING= "host='localhost' dbname='wiki' user='wiki' password='wiki'"
    con=None

    from optparse import OptionParser
    
    # option
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input", dest="inword", 
                help="input string(example:\"Barak Obama\")")
    parser.add_option("-l", "--lang",dest="lang",
                help="language (one of EN|RU|ES|FA)")
    parser.add_option("-s", "--substring", dest="substring", action="store_true",
                  help="match input string as substring (default is exact match)",
                  default=False)
    parser.add_option("-c", "--casesensitive", dest="case_sensitive", action="store_true",
                  help="match input string as case-sensitive (default is case-insensitive)",
                  default=False)
    parser.add_option("-p", "--preferredmeaning", dest="preferred_meaning", action="store_true",
                  help="return preferred meaning of category (default is NOT preferred)",
                  default=False)
    (options, args) = parser.parse_args()
    
    if not options.inword:
        parser.error("Must supply input string. (Example: -i \"Barack Obama\")")
    if not options.lang:
        parser.error("Must supply language. (Examplae: -l EN ; allowed languages: EN|ES|RU|FA)")

    inword=options.inword
    inword=inword.replace(" ","_")
    lang=options.lang
    substring=options.substring
    case_sensitive=options.case_sensitive
    preferred_meaning=options.preferred_meaning
    # currently, implement the preferred_meaning as exact search.
    if preferred_meaning:
        substring = False
    
    #prepare language suffix for yago and yago
    langIndex={"EN":0,"ES":1,"RU":2,"FA":3}
    qlangs=['@eng','@spa','@rus','@fas']
    wlangs=['@en','@es','@ru','@fa']
    tables=['wiki_en','wiki_es','wiki_ru','wiki_fa']
    lindex=langIndex[lang]
    qlang=qlangs[lindex]
    wlang=wlangs[lindex]
    table_name=tables[lindex]
    
       
    query = "select title,abstract from TABLE_NAME where title ilike '@@@word@@@'"
    query = query.replace('TABLE_NAME',table_name)

    #prepare search word
    if substring:
        inword = '%'+inword+'%'
    else:
    #exact match
        inword = inword
            
    #build query
    if ( not case_sensitive ) and ( not substring ): #exact match
        query = query.replace("ilike","=")
    if case_sensitive:
        query = query.replace('ilike','like')
       
    if preferred_meaning: # still do not know how to deal with?
        query = query.replace("yf2.predicate='rdfs:label'","yf2.predicate='<isPreferredMeaningOf>'")
    
    query = query.replace('@@@word@@@',inword)
    print "Query:",query

    try:
        # change CONN_STRING accordingly.
        con = psycopg2.connect(CONN_STRING) 
        con.set_client_encoding('UTF8')
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        #get result
        rows = cur.fetchall()
        i=0
        for row in rows:
            i+=1
            print '#'+str(i)+" TITLE: "+row['title']
            print '#'+str(i)+" ABSTRACT: "+row['abstract']
        
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    main()
