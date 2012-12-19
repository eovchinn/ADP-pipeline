#!/bin/bash

#for henry
echo install git
sudo apt-get install git-core
sudo apt-get install g++

echo install sqlite
sudo apt-get install libsqlite3-dev

echo install python related packages
#sudo apt-get install python
sudo apt-get install python-dev
sudo apt-get install python-lxml
sudo apt-get install python-nltk

echo install graphviz
sudo apt-get install graphviz

#for boxer
echo installing subversion
sudo apt-get install subversion

echo installing SWI Prolog
sudo apt-get install gprolog swi-prolog

echo updating nltk
git clone git://github.com/nltk/nltk.git
cd nltk
sudo python setup.py install

