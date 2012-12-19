#!/bin/bash

#for henry
echo install git
sudo port install git-core

echo install sqlite
sudo port install sqlite3

echo install python related packages
sudo port install python27
sudo easy_install lxml

echo install graphviz
sudo port install graphviz

#for boxer
echo installing subversion
sudo port install subversion

echo installing SWI Prolog
sudo port install gprolog
sudo port install swi-prolog

echo installing wget
sudo port install wget

echo updating nltk
git clone git://github.com/nltk/nltk.git
cd nltk
sudo python setup.py install

