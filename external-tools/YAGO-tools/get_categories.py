#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import sys
import codecs

CONN_STRING =  "host='localhost' dbname='yago' user='yago' password='yago'"
con = None

def main():

  query="select distinct subject, object from yagofacts where subject like '%@@@word@@@%'and predicate like 'rdf:type'"

  #get inputs
  args=sys.argv
  if len(args)!=3:
	print "Usage:" , args[0],  "\"word\" lang<EN|RU|FA|ES>"
	print "Example:" , args[0],  "\"Barack Obama\" EN"
	sys.exit(0)

  inword=args[1]
  lang=args[2]

  #replace spaces with _
  inword = inword.replace(' ','_')
  #build query
  query = query.replace('@@@word@@@',inword)
  print "Query:",query

  try:
    con = psycopg2.connect(CONN_STRING) 
    con.set_client_encoding('UTF8')
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    #get result
    rows = cur.fetchall()
    for row in rows:
    	#print row['subject'],row['object']
    	print row['object']

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

if __name__ == "__main__":
	main()

