#!/bin/bash

echo install henry
cd $ADP_HOME
rm -f -r henry-n700
git clone https://github.com/naoya-i/henry-n700.git

echo compile henry
cd $ADP_HOME/henry-n700
make