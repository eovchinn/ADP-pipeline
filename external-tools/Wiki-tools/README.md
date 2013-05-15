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

* Download long_abstracts_es.nt.bz2:http://downloads.dbpedia.org/3.8/es/long_abstracts_es.nt.bz2

* Download long_abstracts_ru.nt.bz2:http://downloads.dbpedia.org/3.8/ru/long_abstracts_ru.nt.bz2

* Download long_abstracts_fa.nt.bz2:http://downloads.dbpedia.org/3.8/fa/long_abstracts_fa.nt.bz2

* Download Bijective Inter-Language Links:http://downloads.dbpedia.org/3.8/en/interlanguage_links_same_as_en.nt.bz2

* Uncompress the *.bz2 files

```
bzip2 -d long_abstracts_*.bz2 
```

#### Import DBpedia Dataset into Database

* Install psycopg2 library (for connecting to PostgreSQL)

```
sudo apt-get install python-psycopg2
```

* Edit Connect String

In global_setting.py edit CONN_STRING to reflect your database
settings.

* Insert the data into PostgreSQL database

* Edit the DOWNLOAD_DIR in insertAll2DB.sh to where you download all the *.nt files
```
bash insertAll2DB.sh
```


* Build the Index
```
python buildIndex.py
```

* process the Bijective Inter-Language Link:
```
python process_bijective_link.py -d DIR_PATH
```

### Download the Yago Database

* Download yagoLabels:http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoLabels.tsv.7z

* Download yagoMultilingualInstanceLabels:http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoMultilingualInstanceLabels.tsv.7z

* Download yagoMultilingualClassLabels:http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoMultilingualClassLabels.tsv.7z

* Download yagoWikipediaInfo: http://www.mpi-inf.mpg.de/yago-naga/yago/download/yago/yagoWikipediaInfo.tsv.7z




* import tsv files into database 
```
psql -a -d 'wiki' -h 'localhost' -U 'wiki' -f importYago.sql
```

### Test data imported
```
psql -d yago
\dt 
\di
```
should contains 6 relevent tables and 20 relevant indexes.


### Extract the first paragraph of wiki: get_paragraph.py

* Edit Connect String

In global_setting.py edit CONN_STRING to reflect your database
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

### Similarity Tools using Wordnet

#### Setup NLTK tools

* Download and install nltk on your machine. Here is the guide : http://nltk.org/install.html

* Download NLTK Data: wordnet corpus.
```
python
import nltk
nltk.download()
```
In the new window, find corpus->wordnet, and click Download.

#### set up ConceptNet tools

* Create conceptnet database and user

```
sudo su root
su - postgres
psql
postgres=# create database wiki;
postgres=#  GRANT ALL PRIVILEGES ON DATABASE wiki to wiki;
postgres=# \q
```

* Download the conceptnet database: http://conceptnet5.media.mit.edu/downloads/current/conceptnet5.1.2-20121212-csv.tar.bz2

* Extract all files to a Directory, let's call this directory $cnDIR.

* In build_conceptnet.sh, change CONCEPTNET_DIR to $cnDIR.

* build the conceptnet tables and translation tables.
```
bash build_conceptnet.sh
```

#### Compute Similarity between two words

* Using wordnet's own similarity package

Please refer to http://nltk.googlecode.com/svn/trunk/doc/howto/wordnet.html

* Calculate similarity incorporated with direvationally related form:

Please refer to similarity_all.py demo()

#### similarity method

* similarity.py: the script to call different similarity measure methods

* similarity_wordnet.py: using wordnet's relations: hypernym, hyponym, derivationlly related form, antonyms and similary meanings. Only support for English.

* similarity_conceptnet.py: Using conceptnet's graph to calculate the shortest path between two words. The similarity is 1/ length of the path. Only support for FA,ES,RU. The only issue is that the graph is too sparse and amount of nodes is small, so it often doesn't work.

* similarity_translation.py: Using wiktionary.org' translation information, first translate two words into English, and then call similarity_wordnet.py to calculate similarity between the two English words. Support for ES,FA,RU.

#### Get similarity results for a wiki paragraph

* First, use the get_paragraph.py to find the paragraph which you are interested in, and parse it.
```
python get_paragraph.py -i 'Nation' -l EN --stdout| python parse.py -l --common commonDIR --temp temp/temp.txt EN >temp/nation.txt
```
where commonDIR = $METAPHOR_DIR/pipelines/common

* Use similarity.py to compute similarty:
```
python similarity.py -w nation -p nn -i temp/nation.txt -o temp/nation.rank.txt
```
-w options should follows the target word, and -p options should follow the target word's POS tag, which should be compatible with LF form's suffix, i.e. nn,rb,vb,adj.


```
psql
create database conceptnet;
grant all privileges on database conceptnet to wiki;
```

### known bugs

1. get_paragraph.py: We can not support Russian caseinsensetive option due to 'ilike' in Postgresql is not support with Russian. So please initalized the first letter when you deal with Russian.

2. similarity.py: Can not support Farsi, for we need to read .obs file to get the predicate. However, these predicate is not native Farsi, but some English-letters, so can not calculate similarity.

