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

```
python get_categories.py "string" lang<EN|ES|RU|FA> <-s>
```
-s: substring match; default is exact match

example exact match:
```
python get_categories.py "Barack Obama" EN
```
example substring match:
```
python get_categories.py "Barack Obama" EN -s
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

returns:
```
{'<wordnet_person_100007846>': 
set(['<wordnet_economist_110043643>', '<wordnet_alumnus_109786338>', '<wordnet_narrator_110345804>', 
'<wordnet_writer_110794014>', '<wordnet_laureate_110249011>', '<wordnet_statesman_110650162>', 
'<wordnet_atheist_109820044>', '<wordnet_person_100007846>', '<wordnet_academician_109759069>', 
'<wordnet_president_110467179>', '<wordnet_lawyer_110249950>', '<wordnet_senator_110578471>', 
'<wordnet_organizer_110383237>', '<wordnet_politician_110451263>', '<wordnet_scholar_110557854>', 
'<wordnet_state_senator_110650076>', '<wordnet_officeholder_110371450>']), 
'<yagoGeoEntity>': 
set(['<wordnet_position_108621598>']), 
'<wordnet_abstraction_100002137>': 
set(['<wordnet_meme_105985126>', '<wordnet_controversy_107183151>', '<wordnet_address_107238694>', 
'<wordnet_theory_105989479>', '<wordnet_inauguration_100239910>', '<wordnet_attempt_100786195>', 
'<wordnet_tenure_115291498>', '<wordnet_image_105928118>']), 
'<wordnet_organization_108008335>': 
set(['<wordnet_secondary_school_108284481>', '<wordnet_organization_108008335>', '<wordnet_school_108276720>', 
'<wordnet_senior_high_school_108409617>']), 
'owl:Thing': 
set(['<wordnet_organization_108008335>', '<wordnet_person_100007846>']), 
'<wordnet_artifact_100021939>': 
set(['<wordnet_oeuvre_103841417>', '<wordnet_book_106410904>'])}

```
