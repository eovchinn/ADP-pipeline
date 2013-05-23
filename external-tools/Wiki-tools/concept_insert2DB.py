import mydb
import os


def create_table(con,table_name):
    querys = []
    query = 'drop table if exists __table_name__;'
    query = query.replace('__table_name__',table_name)
    querys.append(query)
    query = 'create table __table_name__(rel text, s text, e text);'
    query = query.replace('__table_name__',table_name)
    querys.append(query)
    mydb.executeManyQuery(con,querys,True)


def insert_records(con,table_name,fileName,lang):
    cn_lang = {'EN':'en','RU':'ru','FA':'fa','ES':'es'}
    prefix = '/c/'+cn_lang[lang]+'/'
    f = open(fileName,'r')
    f.readline()
    records = []
    buffer_size = 100
    query = 'insert into __table_name__(rel,s,e) values(%s,%s,%s)'
    query = query.replace('__table_name__',table_name)
    i = 0
    for line in f:
        line = line.decode('utf8')
        ll = line.split('\t')
        tri = ll[0][4:-1]
        tris = tri.split(',')
        
        # check for language
        if not (tris[1].startswith(prefix) and tris[2].startswith(prefix)):
            continue

        i+=1
        if i%10000 == 0:
            print i

        record = (tris[0],tris[1],tris[2])
        records.append(record)
        
        if len(records) > buffer_size:
            mydb.executeQueryRecords(con,query,records,False)
            records = []

    if len(records) > 0:
        mydb.executeQueryRecords(con,query,records,False)
        records = []
    print i
    return i


def insertTranslation(con,table_name,fileName,lang):
    cn_lang = {'EN':'en','RU':'ru','FA':'fa','ES':'es'}
    prefix = '/c/'+cn_lang[lang]+'/'
    en_prefix = '/c/'+cn_lang['EN']+'/'

    f = open(fileName,'r')
    f.readline()
    records = []
    buffer_size = 100
    query = 'insert into __table_name__(rel,s,e) values(%s,%s,%s)'
    query = query.replace('__table_name__',table_name)
    i = 0
    for line in f:
        line = line.decode('utf8')
        ll = line.split('\t')
        tri = ll[0][4:-1]
        tris = tri.split(',')
        
        # check for language
        if not (tris[0]== '/r/TranslationOf/' and (tris[1].startswith(prefix) and tris[2].startswith(en_prefix)) ):
            continue

        i+=1
        if i%10000 == 0:
            print i

        record = (tris[0],tris[1],tris[2])
        records.append(record)
        
        if len(records) > buffer_size:
            mydb.executeQueryRecords(con,query,records,False)
            records = []

    if len(records) > 0:
        mydb.executeQueryRecords(con,query,records,False)
        records = []
    print i
    return i


def processConceptNet(lang,dirPath):
    # prepare DB
    CONN_STRING = "host='localhost' dbname='conceptnet' user='wiki' password='wiki'"
    con = mydb.getCon(CONN_STRING)
    table_name = 'cn_'+lang
    create_table(con, table_name)

    #process and insert file
    sum = 0
    dirPath = os.path.abspath(dirPath)
    for file in os.listdir(dirPath):
        if file.endswith('.csv'):
            if '_zh_' in file or '_nadya_' in file:
                continue
            #if file == 'dbpedia.9.csv':
            else:
                print file
                sum+=insert_records(con,table_name,os.path.join(dirPath,file),lang)
    
    print sum


def processTranslation(lang,dirPath):
    # prepare DB
    CONN_STRING = "host='localhost' dbname='conceptnet' user='wiki' password='wiki'"
    con = mydb.getCon(CONN_STRING)
    table_name = 'translation_'+lang
    create_table(con, table_name)

    #process and insert file
    sum = 0
    dirPath = os.path.abspath(dirPath)
    file = 'wiktionary.csv'
    print file
    sum+=insertTranslation(con,table_name,os.path.join(dirPath,file),lang)
    
    print sum


def main():
    
    from optparse import OptionParser
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    parser.add_option("-d","--dir",dest='dir',help = "the csv dir path")
    (options,args) = parser.parse_args()
    lang = options.lang
    dirPath = options.dir
    processConceptNet(lang,dirPath)
    processTranslation(lang,dirPath)

if __name__ == '__main__':
    main()
