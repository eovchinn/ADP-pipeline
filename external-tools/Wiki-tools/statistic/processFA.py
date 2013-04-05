#!/usr/bin/python
# -*- coding: utf-8 -*-

import mydb

CONN_STRING = mydb.get_CONN()
con = mydb.getCon(CONN_STRING)

query = "select distinct value from property_fa where property = '<http://fa.dbpedia.org/property/type>'"

rows = mydb.executeQueryResult(con,query,True)

file = open('types_fa.txt','w')

print len(rows)
for row in rows:
    file.write(row[0]+'\n')

file.close()
