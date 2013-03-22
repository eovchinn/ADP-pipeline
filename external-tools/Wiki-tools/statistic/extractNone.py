
import mydb
import sys

typeFile = open('es_property.txt','r')
transFile = open('es_property_translate.txt','r')

CONN_STRING = mydb.get_CONN()
con = mydb.getCon(CONN_STRING)


while True:
    type = typeFile.readline()
    if not type:
        break
    trans = transFile.readline()
    type = type.strip()
    trans = trans.strip()
    query = "update statistic_es set native_property = '__trans__' where property = '__type__' "
    query = query . replace ('__trans__',trans)
    query = query . replace ('__type__',type)
    mydb.executeQuery(con,query,True)


    
