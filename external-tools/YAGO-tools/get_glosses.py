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
parser.add_option("-c", "--casesensitive", dest="case_sensitive", action="store_true",
                  help="match input string as case-sensitive (default is case-insensitive)",
                  default=False)
parser.add_option("-p", "--preferredmeaning", dest="preferred_meaning", action="store_true",
                  help="return preferred meaning of category (default is NOT preferred)",
                  default=False)
(options, args) = parser.parse_args()

def main():

  #using distinct and only the category as output will not give duplicates
  query="(select distinct yf1.subject as subject, yf1.object as category, yf3.object as gloss from yagofacts yf1, yagofacts yf2, yagofacts yf3 where yf2.predicate='rdfs:label' and yf2.object ilike '@@@word@@@' and yf2.subject=yf1.subject and yf1.predicate='rdf:type' and yf1.object=yf3.subject and yf3.predicate='<hasGloss>' and yf3.object like '%@@@lang@@@') UNION (select distinct yf2.object as subject, yf2.subject as category, yf3.object as gloss from yagofacts yf2, yagofacts yf3 where yf2.object ilike '@@@word@@@' and yf2.predicate='rdfs:label' and yf2.subject=yf3.subject and yf3.predicate='<hasGloss>' and yf3.object like '%@@@lang@@@')"

  if not options.inword:
    parser.error("Must supply input string. (Example: -i \"Barack Obama\")")
  if not options.lang:
    parser.error("Must supply language. (Examplae: -l EN ; allowed languages: EN|ES|RU|FA)")

  inword=options.inword
  lang=options.lang
  substring=options.substring
  case_sensitive=options.case_sensitive
  preferred_meaning=options.preferred_meaning

  #prepare language
  qlang=None
  if lang=='RU':
    qlang='@rus'
  elif lang=='ES':
    qlang='@spa'
  elif lang=='FA':
    qlang='@fas'
  elif lang=='EN':
    qlang='@eng'

  #prepare search word
  query = query
  if substring:
    inword = '%'+inword+'%'+qlang
  else:
    #exact match
    inword = '"'+inword+'"'+qlang

  #build query
  if case_sensitive:
    query = query.replace('ilike','like')
  if preferred_meaning:
    query = query.replace("yf2.predicate='rdfs:label'","yf2.predicate='<isPreferredMeaningOf>'")
  query = query.replace('@@@word@@@',inword)
  query = query.replace('@@@lang@@@',qlang)
  print "Query:",query


  try:
    con = psycopg2.connect(CONN_STRING) 
    con.set_client_encoding('UTF8')
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    #get result
    rows = cur.fetchall()
    glosses={}
    for row in rows:
        #print row['subject'],row['category'],row['gloss']
        gloss_list = glosses.get(row['subject'])
        if gloss_list is None:
          #first gloss for this subject
          gloss_list = set()
          glosses[row['subject']] = gloss_list

        gloss_list.add(row['gloss'])

    print glosses

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

if __name__ == "__main__":
	main()

