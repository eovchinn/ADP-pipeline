#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import sys
import codecs

CONN_STRING =  "host='localhost' dbname='yago' user='yago' password='yago'"
con = None

def main():

  query_eng="select distinct yf1.subject as subject, yf1.object as category, yf2.object as supercategory from yagofacts yf1, yagofacts yf2 where yf1.subject like '@@@word@@@'and yf1.predicate='rdf:type' and yf1.object=yf2.subject and yf2.predicate='rdfs:subClassOf'"
  query_multi="select distinct yf2.object as subject, yf1.object as category, yf3.object as supercategory from yagofacts yf1, yagofacts yf2, yagofacts yf3 where yf2.predicate='rdfs:label' and yf2.object like '@@@word@@@' and yf2.subject=yf1.subject and yf1.predicate='rdf:type' and yf1.object=yf3.subject and yf3.predicate='rdfs:subClassOf'"

  #get inputs
  args=sys.argv
  if len(args)<3:
	print "Usage:" , args[0],  "\"word\" lang<EN|RU|FA|ES> <-s(optional)>"
	print "Example:" , args[0],  "\"Barack Obama\" EN (exact match)"
	print "Example:" , args[0],  "\"Barack Obama\" EN -s (substring match)"
	sys.exit(0)

  # default is exact match
  substring=False
  if len(args)==4:
    #substring match
    if args[3]=='-s':
      substring=True

  inword=args[1]
  lang=args[2]

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
    	print row['subject'],row['category'],row['supercategory']

    #key=supercategory; value=list of subcategories
    supercategories = {}
    for row in rows:
      category_list = supercategories.get(row['supercategory'])
      if category_list is None:
        #first category for this supercategory
        category_list = set()
        supercategories[row['supercategory']] = category_list

      category_list.add(row['category'])

    print supercategories

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

if __name__ == "__main__":
	main()

