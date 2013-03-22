### Statisitc about wikipedia inforbox property

* Note: supported language: English,Russian and Spanish

* import the table into database

run the following command:(Assume you have a PostSQL database named 'wiki' and a user named 'wiki')

```
psql -a -d 'wiki' -h 'localhost' -U 'wiki' -f statistic.sql
```

There would be 3 tables: statistic_en, statistic_es, statistic_ru, the schema of each table is as following:

```
    type character varying,
    property character varying,
    native_type character varying,
    native_property character varying,
    hit integer,
    total integer 
```
