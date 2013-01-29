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
parser.add_option("-r", "--relations",dest="relations",
                  default="allRelations",
                help="list of relations (example:\"<hasName>,<hasGender>,...\"; default is \"allRelations\")")
(options, args) = parser.parse_args()

def main():

  query="select distinct yf2.object as instring, yf2.object as subject, yf1.object as object, yf1.predicate as relation from yagofacts yf1, yagofacts yf2 where yf2.predicate='rdfs:label' and yf2.object ilike '@@@word@@@' and yf2.subject=yf1.subject and @@@relation_list@@@"
  query_all_relations="select distinct yf2.object as instring, yf2.subject as subject, yf1.object as object, yf1.predicate as relation from yagofacts yf1, yagofacts yf2 where yf2.predicate='rdfs:label' and yf2.object ilike '@@@word@@@' and yf2.subject=yf1.subject and yf1.predicate not like 'rdf:type' and yf1.predicate not like 'rdfs:label'"

  if not options.inword:
    parser.error("Must supply input string. (Example: -i \"Barack Obama\")")
  if not options.lang:
    parser.error("Must supply language. (Examplae: -l EN ; allowed languages: EN|ES|RU|FA)")

  inword=options.inword
  lang=options.lang
  substring=options.substring
  relations=options.relations
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

  query = query
  if relations=='allRelations':
    query=query_all_relations

  #prepare search word
  if substring:
    inword = '%'+inword+'%'+qlang
  else:
    #exact match
    inword = '"'+inword+'"'+qlang


  #prepare relation list
  relation_names=[s.strip() for s in relations.split(',')]
  relation_list="("
  i=0
  for r in relation_names:
    if i!=0:
      relation_list += " or "
    relation_list += "yf1.predicate='" + r + "'"
    i+=1
  relation_list += ")"

  #build query
  if case_sensitive:
    query = query.replace('ilike','like')
  if preferred_meaning:
    query = query.replace("yf2.predicate='rdfs:label'","yf2.predicate='<isPreferredMeaningOf>'")
  query = query.replace('@@@word@@@',inword)
  query = query.replace('@@@relation_list@@@',relation_list)
  print "Query:",query

  try:
    con = psycopg2.connect(CONN_STRING) 
    con.set_client_encoding('UTF8')
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    #get result
    rows = cur.fetchall()
    """    
    print 'instring','subject,','relation,','object'
    for row in rows:
    	print row['instring'],row['subject'],row['relation'],row['object']
    """

    #key=relation; value=list of objects
    #relations = {}
    #key=subject; value=relations dictionary
    subjects = {}
    for row in rows:
      if  not row['relation'].startswith("<"): 
         continue;
      #key=relation; value=list of objects
      relations = subjects.get(row['subject'])
      if relations is None:
        #first relation for this subject
        relations = {}
        subjects[row['subject']] = relations
      objects = relations.get(row['relation'])
      if objects is None:
        #first object for this relation
        objects = set()
        relations[row['relation']] = objects

      objects.add(row['object'])

    print subjects

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

if __name__ == "__main__":
  main()

