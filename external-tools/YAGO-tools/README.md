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

### Extract SIMPLETAX categories

* Install psycopg2 library (for connecting to PostgreSQL)

```
sudo apt-get install python-psycopg2
```
* Edit Connect String

In get_categories.py edit CONN_STRING to reflect your database
settings.

* Run program

```
python get_categories.py "string" lang<EN|ES|RU|FA>
```

example:
```
python get_categories.py "Barack Obama" EN
```

returns:

...

&lt;wordnet_scholar_110557854&gt;

&lt;wordnet_person_100007846&gt;

&lt;wordnet_person_100007846&gt;

&lt;wordnet_writer_110794014&gt;

...


