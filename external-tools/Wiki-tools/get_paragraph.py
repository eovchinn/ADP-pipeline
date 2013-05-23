#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import codecs
import psycopg2.extras
import get_paragraph_prefer
import global_setting

class setting:
    inword=''
    substring = False
    case_sensitive = False
    preferred_meaning = False
    qlang = ''
    wlang = ''
    table_name=''
    lang = ''
    CONN_STRING = ''
    debug = False

def main():
    # database settings
    CONN_STRING= global_setting.get_CONN()
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
    parser.add_option("-d","--debug",dest = "debug" , action = "store_true",
                  help="output debug info, default is false", default = False)
    parser.add_option("--stdout",dest = 'stdout', action = 'store_true',help='direct write the output to stdout',default = False)
    (options, args) = parser.parse_args()
    
    if not options.inword:
        parser.error("Must supply input string. (Example: -i \"Barack Obama\")")
    if not options.lang:
        parser.error("Must supply language. (Examplae: -l EN ; allowed languages: EN|ES|RU|FA)")

    inword=options.inword
    lang=options.lang
    substring=options.substring
    case_sensitive=options.case_sensitive
    preferred_meaning=options.preferred_meaning
    debug = options.debug
    stdout = options.stdout
    #prepare language suffix for yago and yago
    langIndex={"EN":0,"ES":1,"RU":2,"FA":3}
    qlangs=['@eng','@spa','@rus','@fas']
    wlangs=['@en','@es','@ru','@fa']
    tables=['wiki_en','wiki_es','wiki_ru','wiki_fa']
    lindex=langIndex[lang]
    qlang=qlangs[lindex]
    wlang=wlangs[lindex]
    table_name=tables[lindex]
    
    if preferred_meaning: 
        myset = setting()
        myset.inword= inword
        myset.substring = substring
        myset.case_sensitive = case_sensitive
        myset.preferred_meaning = preferred_meaning
        myset.qlang = qlang
        myset.wlang = wlang
        myset.table_name= table_name
        myset.lang = lang
        myset.CONN_STRING = CONN_STRING
        myset.debug = debug
        goon = get_paragraph_prefer.prefer_search(myset)
        if goon == 0:
            return 0
    
    inword=inword.replace(" ","_")
    query = "select title,abstract from TABLE_NAME where title ilike '@@@word@@@'"
    query = query.replace('TABLE_NAME',table_name)

    #prepare search word
    if substring:
        inword = '%'+inword+'%'
    else:
    #exact match
        inword = inword
            
    #build query
    if case_sensitive and ( not substring ): #exact match
        query = query.replace("ilike","=")
    if case_sensitive:
        query = query.replace('ilike','like')
        
    query = query.replace('@@@word@@@',inword)
    if debug:
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
        if not stdout:
            for row in rows:
                i+=1
                print '#'+str(i)+" TITLE: "+row['title']
                print '#'+str(i)+" ABSTRACT: "+row['abstract']
        else:
            if len(rows)>0:
                print rows[0]['abstract']
            else:
                print 'no result!'
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    main()
