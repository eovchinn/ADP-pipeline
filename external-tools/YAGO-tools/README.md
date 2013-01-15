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

in /etc/postgresql/9.1/main/pg_hba.conf
add this line (this gives access to ISI network):
```
# TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD
host    postgres    all         128.9.0.0/16          md5
```

in /etc/postgresql/9.1/main/postgresql.conf
add this:
```
listen_addresses='*'
port=5432
```

NOTE: Sometimes these files are found in: /var/lib/pgsql/data/


* Restart Database
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
`su - yago` ( pwd is yago)

`psql -d yago` (connect to database yago)

`\dt` (list the tables)

Should contain one table "yagofacts"

