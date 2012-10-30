#!/bin/bash

if [ $# != 1 ]; then
echo Usage: "$0 install_dir"
exit 1
fi

install_dir=$1
export ADP_HOME=$install_dir

source ./setenv-mac.sh

echo install henry

cd $ADP_HOME
rm -f -r henry-n700
git clone https://github.com/naoya-i/henry-n700.git

echo compile henry
cd $ADP_HOME/henry-n700
make