
#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import global_setting

def buildIndex():
    
    CONN_STRING= global_setting.get_CONN()
    con = None
    try:
        con = psycopg2.connect(CONN_STRING)
        con.set_client_encoding('UTF8')
        cur = con.cursor()
        
        # build index on title
        
        langs=['en','es','ru','fa']
        for lang in langs:
            query1 = 'CREATE INDEX '+lang+'IndexTitle ON wiki_'+lang+'(title)'
            query2 = 'CREATE INDEX '+lang+'IndexLowerTitle ON wiki_'+lang+'(lower(title))'
            print query1
            cur.execute(query1)
            con.commit()
            print query2
            cur.execute(query2)
            con.commit()
            
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)
    
    if con:
        con.close()

if __name__ == "__main__":
   buildIndex()
