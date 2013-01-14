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
su - postgres
psql
postgres=# create user yago with password 'yago';
CREATE ROLE
postgres=# create database yago;
CREATE DATABASE
postgres=#  GRANT ALL PRIVILEGES ON DATABASE yago to yago;
GRANT
postgres=# \q
```
#### Download SIMPLETEX Theme

