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

  query_eng="select distinct yf1.subject as subject, yf1.object as category, yf2.object as supercategory from yagofacts yf1, yagofacts yf2 where yf1.subject like '@@@word@@@'and yf1.predicate='rdf:type' and yf1.object=yf2.subject and yf2.predicate='rdfs:subClassOf'"
  query_multi="select distinct yf2.object as subject, yf1.object as category, yf3.object as supercategory from yagofacts yf1, yagofacts yf2, yagofacts yf3 where yf2.predicate='rdfs:label' and yf2.object like '@@@word@@@' and yf2.subject=yf1.subject and yf1.predicate='rdf:type' and yf1.object=yf3.subject and yf3.predicate='rdfs:subClassOf'"

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
    """
    print 'subject,','category,','supercategory'
    for row in rows:
    	print row['subject'],row['category'],row['supercategory']
    """

    #parse database output and get a first set of categories and their direct supercategories
    #key=category; value=list of supercategories
    supercategories = {}
    for row in rows:
      supercategory_list = supercategories.get(row['category'])
      if supercategory_list is None:
        #first supercategory for this category
        supercategory_list = set()
        supercategories[row['category']] = supercategory_list

      if row['category']!=row['supercategory']:
        #add only supercategories that are different that the category
        supercategory_list.add(row['supercategory'])

    #one more pass to get all parent supercategories(recursively)
    supercategories_final = {}
    # for each category
    for key in supercategories.keys():
      supercategory_list = supercategories[key]
      # I will add all other supercategories (recursively) to this list
      all_supercategories = supercategory_list.copy()
      for superc in supercategory_list:
        #add all supercategories of superc
        add_superc(superc, supercategories, all_supercategories)

      #the final list of supercategories for this category
      supercategories_final[key] = all_supercategories

    print supercategories_final

  except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
  finally:
    if con:
        con.close()

#add to all_supercategories, all supercategories of category
#supercategories: key=category; value = list of DIRECT supercategories
def add_superc(category, supercategories, all_supercategories):
  direct_superc = supercategories.get(category)
  if direct_superc is None:
    #I am done with this category
    return
  for superc in direct_superc:
    all_supercategories.add(superc)
    add_superc(superc, supercategories, all_supercategories)


if __name__ == "__main__":
	main()

