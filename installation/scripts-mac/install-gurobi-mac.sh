#!/bin/bash

if [ $# != 2 ]; then
echo Usage: "$0 gurobi_file_location gurobi_license_key"
exit 1
fi

echo installing GUROBI ...

gurobi_file=$1
gurobi_license_key=$2
echo Gurobi file: $gurobi_file
echo Gurobi key: $gurobi_license_key

sudo installer -pkg $gurobi_file -target /

echo generating Gurobi license file ...
echo When asked for location of license key file enter $ADP_HOME.
echo If different location is entered modify GRB_LICENSE_FILE in setenv.sh.
echo Press [ENTER]
read enter

#generate license file
grbgetkey $gurobi_license_key
