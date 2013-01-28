#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import sys
import codecs
from optparse import OptionParser

CONN_STRING =  "host='localhost' dbname='yago' user='yago' password='yago'"
con = None

#options
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--input", dest="inword", 
                help="input string(example:\"Barak Obama\")")
parser.add_option("-l", "--lang",dest="lang",
                help="language (one of EN|RU|ES|FA)")
parser.add_option("-s", "--substring", dest="substring", action="store_true",
                  help="match input string as substring (default is exact match)",
                  default=False)
(options, args) = parser.parse_args()

def main():

  query_eng="select distinct subject as subject, object as category from yagofacts where subject like '@@@word@@@'and predicate like 'rdf:type'"
  query_multi="select distinct yf2.object as subject, yf1.object as category from yagofacts yf1, yagofacts yf2 where yf2.predicate like 'rdfs:label' and yf2.object like '@@@word@@@' and yf2.subject like yf1.subject and yf1.predicate like 'rdf:type'"

  if not options.inword:
    parser.error("Must supply input string. (Example: -i \"Barack Obama\")")
  if not options.lang:
    parser.error("Must supply language. (Examplae: -l EN ; allowed languages: EN|ES|RU|FA)")

  inword=options.inword
  lang=options.lang
  substring=options.substring

  #prepare language
  qlang=None
  if lang=='RU':
    qlang='@rus'
  elif lang=='ES':
    qlang='@spa'
  elif lang=='FA':
    qlang='@fas'

  #prepare search word
  if lang=='EN':
    query=query_eng
    #replace spaces with _ only for EN
    inword = inword.replace(' ','\_')
    if substring:
      inword = '%'+inword+'%'
    else:
      #exact match
      inword = '<'+inword+'>'
  else:
    query = query_multi
    if substring:
      inword = '%'+inword+'%'+qlang
    else:
      #exact match
      inword = '"'+inword+'"'+qlang

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
    	print row['subject'],row['category']

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

if __name__ == "__main__":
	main()

