### YAGO Installation Instructions

#### Set Up PostgreSQL Database for YAGO

* Install PostgreSQL
```
sudo apt-get install postgresql
```

* Create a local user
```
sudo adduser yago --no-create-home
```

* Create YAGO database and user
```
sudo su root
su - postgres
psql
postgres=# create user yago with password 'yago';
postgres=# create database yago;
postgres=#  GRANT ALL PRIVILEGES ON DATABASE yago to yago;
postgres=# \q
```

* Open database port 

NOTE: This step is needed if you plan to give outside access to the database. If you plan to use it from localhost this step is not needed.

Example for giving access to ISI network:

in /etc/postgresql/9.1/main/pg_hba.conf
add this line (this gives access to ISI network):
```
# TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD
host    all    all         128.9.0.0/16          md5
```

in /etc/postgresql/9.1/main/postgresql.conf
add this:
```
listen_addresses='*'
port=5432
```

NOTE: Sometimes these files are found in: /var/lib/pgsql/data/


* Restart Database

If at this point you are "postgres" or "yago" user, su to a user that has root access (you can use "exit" command to go back to previous user). Then restart database:
```
sudo  etc/init.d/postgresql restart
```



* Done with database setup

#### Download SIMPLETEX Theme

* Download yagoSimpleTaxonomy:http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoSimpleTaxonomy.tsv.7z
* Download yagoSimpleTypes:http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoSimpleTypes.tsv.7z

#### Download MULTILINGUAL Theme

* Download http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoMultilingualInstanceLabels.tsv.7z
* Download http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoMultilingualClassLabels.tsv.7z

#### Download Database Importer

* Download: http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/postgres.sql.7z
* Import Data

got to directory of the YAGO TSV files and run:
```
psql -a -d <database> -h <hostname> -U <user> -f <thisScript>
```
example:
```
psql -a -d yago -h localhost -U yago -f postgres.sql
```

#### Test Data Import
`su - yago`

`psql -d yago`

`\dt`

Should contain one table "yagofacts"

### Extract Categories

* Install psycopg2 library (for connecting to PostgreSQL)

```
sudo apt-get install python-psycopg2
```
* Edit Connect String

In get_categories.py edit CONN_STRING to reflect your database
settings.

* Run program

Usage: get_categories.py [options]

* Options:

  * -h, --help (show this help message and exit)
  * -i INWORD, --input=INWORD (input string; example:"Barak Obama")
  * -l LANG, --lang=LANG  (language; one of EN|RU|ES|FA)
  * -s, --substring (match input string as substring; default is exact match)


example exact match:
```
python get_categories.py -i "Barack Obama" -l EN
```
example substring match:
```
python get_categories.py -i "Barack Obama" -l EN -s
```

returns:
```
...
<wordnet_scholar_110557854>
<wordnet_person_100007846>
<wordnet_person_100007846>
<wordnet_writer_110794014>
...
```

### Extract SuperCategories

* Install psycopg2 library (for connecting to PostgreSQL)

```
sudo apt-get install python-psycopg2
```
* Edit Connect String

In get_supercategories.py edit CONN_STRING to reflect your database
settings.

* Run program

```
python get_supercategories.py "string" lang<EN|ES|RU|FA> <-s>
```
-s: substring match; default is exact match

example exact match:
```
python get_supercategories.py "Barack Obama" EN
```
example substring match:
```
python get_supercategories.py "Barack Obama" EN -s
```

Returns a dictionary where key = category and value = list of supercategories.

example:
```
{'<wordnet_state_108654360>': set(['<yagoGeoEntity>']), 
'<wordnet_dish_103206908>': set(['<wordnet_artifact_100021939>']), 
'<wordnet_minister_110320863>': set(['<wordnet_person_100007846>', 'owl:Thing']), 
'<wordnet_city_108524735>': set(['<yagoGeoEntity>']), 
'<wordnet_military_officer_110317007>': set(['<wordnet_person_100007846>', 'owl:Thing']), 
'<wordnet_vodka_107906111>': set(['<wordnet_abstraction_100002137>']),
...}
```
