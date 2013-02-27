### WIKI Installation Instructions

#### Set Up PostgreSQL Database for WIKI

* Install PostgreSQL

```
sudo apt-get install postgresql
```

* Create a local user

```
sudo adduser wiki --no-create-home
```

* Create wiki database and user

```
sudo su root
su - postgres
psql
postgres=# create user wiki with password 'wiki';
postgres=# create database wiki;
postgres=#  GRANT ALL PRIVILEGES ON DATABASE wiki to wiki;
postgres=# \q
```

* Restart Database

If at this point you are "postgres" or "wiki" user, su to a user that has root access (you can use "exit" command to go back to previous user). Then restart database:

```
sudo  etc/init.d/postgresql restart
```

* Done with database setup

#### Download DBPedia Dataset

* Download long_abstracts_en.nt.bz2:http://downloads.dbpedia.org/3.8/en/long_abstracts_en.nt.bz2

* Download long_abstracts_en_uris_es.nt.bz2:http://downloads.dbpedia.org/3.8/es/long_abstracts_en_uris_es.nt.bz2
* Download long_abstracts_es.nt.bz2:http://downloads.dbpedia.org/3.8/es/long_abstracts_es.nt.bz2

* Download long_abstracts_en_uris_ru.nt.bz2:http://downloads.dbpedia.org/3.8/ru/long_abstracts_en_uris_ru.nt.bz2
* Download long_abstracts_ru.nt.bz2:http://downloads.dbpedia.org/3.8/ru/long_abstracts_ru.nt.bz2

* Download long_abstracts_en_uris_fa.nt.bz2:http://downloads.dbpedia.org/3.8/fa/long_abstracts_en_uris_fa.nt.bz2
* Download long_abstracts_fa.nt.bz2:http://downloads.dbpedia.org/3.8/fa/long_abstracts_fa.nt.bz2

* Uncompress the *.bz2 files

```
bzip2 -d long_abstracts_*.bz2 
```

#### Import Dataset into Database

* Install psycopg2 library (for connecting to PostgreSQL)

```
sudo apt-get install python-psycopg2
```

* Edit Connect String

In insertFile2DB.py and buildIndex.py edit CONN_STRING to reflect your database
settings.

* Insert the data into PostgreSQL database

```
python insertAll2DB.py -d DIR_PATH
```

where the DIR_PATH is the directory path where those *.nt files located in.

* Build the Index
```
python buildIndex.py
```

* Test data imported
```
psql -d wiki
\dt 
\di
```
should contains 4 tables and 12 indexes.

### Extract the first paragraph of wiki: get_paragraph.py

* Edit Connect String

In get_paragraph.py edit CONN_STRING to reflect your database
settings.

* Run program

Usage: get_paragraph.py [options]

* Options:
  * -h, --help show this help message and exit
  * -i INWORD, --input=INWORD, input string(example:"Barak Obama")
  * -l LANG, --lang=LANG, language (one of EN|RU|ES|FA)
  * -s, --substring, match input string as substring (default is exact match)
  * -c, --casesensitive, match input string as case-sensitive (default is case-insensitive)
  * -p, --preferredmeaning, return preferred meaning of category (default is NOT preferred)

example exact match, case insensitive:
```
python get_paragraph.py -i "Barack Obama" -l EN
```

example substring match, case insensitive:
```
python get_paragraph.py -i "Barack Obama" -l EN -s
```

example exact match, case sensitive:
```
python get_paragraph.py -i "Barack Obama" -l EN -c
```

returns:

```
 #1 TITLE: Barack_Obama
 #1 ABSTRACT: "Barack Hussein Obama II is the 44th and current President of the United States. He is the first African American to hold the office.
...
...
In foreign policy, he ended the war in Iraq, increased troop levels in Afghanistan, signed the New START arms control treaty with Russia, ordered U.S. involvement in the 2011 Libya military intervention, and ordered the military operation that resulted in the death of Osama bin Laden."@en...
```