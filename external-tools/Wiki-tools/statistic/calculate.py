#!/usr/bin/python
# -*- coding: utf-8 -*-

import mydb


def calculate(type_name,lang):
    result = {}
    indexs={"EN":0,"ES":1,"RU":2,"FA":3}
    type_table_names=["type_en","type_es","type_ru"]
    property_table_names=["property_en","property_es","property_ru"]
    CONN_STRING = mydb.get_CONN()
    con = mydb.getCon(CONN_STRING)
    rows=[]
    property_table_name=''
    type_table_name = ''
    if lang !='FA':
        index = indexs[lang]
        type_table_name = type_table_names[index]
        property_table_name = property_table_names[index]
        type_name = '<'+type_name+'>'
        query = "select entity from __type_table__ where type = '__type_name__'"
        query = query.replace('__type_table__',type_table_name)
        query = query.replace('__type_name__',type_name)
        rows = mydb.executeQueryResult(con,query,True)
        result['__total__']=len(rows)
    else:
        property_table_name = 'property_fa'
        
        query = "select distinct entity from property_fa where property = '<http://fa.dbpedia.org/property/type>' and value ='__type_name__' "
        query = query.replace('__type_name__',type_name)
        rows = mydb.executeQueryResult(con,query,True)
        result['__total__']=len(rows)

    temp_result={}
    print len(rows)
    i=0
    for row in rows:
        entity = row[0]
        entity = entity.replace("'","''")
        query = "select property from __property_table__ where entity = '__entity_name__';"
        query = query.replace('__property_table__',property_table_name)
        query = query.replace('__entity_name__',entity)
        ps = mydb.executeQueryResult(con,query,False)
        for p in ps:
            if not p[0] in temp_result:
                temp_result[p[0]]=1
        for p in temp_result:
            if not p in result:
                result[p]=0
            result[p]+=1
        temp_result={}
        i+=1
        if i % 50 ==0:
            print i
    #print result
    return result



    
def main():
    from optparse import OptionParser
    #option
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--type", dest="type_name",help="type name")
    parser.add_option('-l','--lang',dest='lang',help="language")
    (options,args) = parser.parse_args()

    lang = options.lang
    type_name = options.type_name

    calculate(type_name,lang)

if __name__ == '__main__':
    main()
   
    





