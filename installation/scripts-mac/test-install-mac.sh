#!/bin/bash

if [ $# != 1 ]; then
echo Usage: "$0 install_dir"
exit 1
fi

echo testing henry

install_dir=$1
export ADP_HOME=$install_dir

source ./setenv-mac.sh

mkdir -p $ADP_HOME/test
cd $ADP_HOME/henry-n700

./bin/henry -m infer -e models/h93.py -O proofgraph toy/hello.lisp > $ADP_HOME/test/out.henry

python tools/proofgraph.py --input $ADP_HOME/test/out.henry --graph lingheu | dot -T pdf > $ADP_HOME/test/out.henry.pdf

echo Henry output in: $ADP_HOME/test
