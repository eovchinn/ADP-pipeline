#!/bin/bash

if [ $# != 3 ]; then
echo Usage: "$0 boxer_username boxer_password boxer_models"
exit 1
fi

echo installing BOXER ...

boxer_username=$1
boxer_password=$2
boxer_models=$3

svn co http://svn.ask.it.usyd.edu.au/candc/trunk $ADP_HOME/boxer --username $boxer_username --password $boxer_password

cd $ADP_HOME/boxer
ln -s Makefile.macosx Makefile
make
make bin/boxer
make bin/tokkie

echo unpack models
#in mac it's .tar because it is unzipped when downloaded
cp $boxer_models .
tar -xzf models*.*
rm -f models*.*

