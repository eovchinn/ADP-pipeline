#!/usr/bin/python

import os
import sys

if len(sys.argv)!=2:
    print("Usage:" + sys.argv[0] + " install_dir")
    sys.exit()

install_dir=sys.argv[1]

setvars = raw_input("This script modifies your .bash_profile file, and sets environment variables relevant for this application. Continue? [yes/no]")

if setvars == "yes": 

    bashrc_file=os.environ['HOME'] + "/.bash_profile"

    f=open(bashrc_file, "a+")
    
    f.write("\n#Metaphor ADP\n")
    f.write("export ADP_HOME="+install_dir+"\n")
    f.write("export GUROBI_HOME=/Library/gurobi511/mac64\n")
    f.write("export GRB_LICENSE_FILE=$ADP_HOME/gurobi.lic\n")

    if os.environ.get('PATH') is None:
        f.write("export PATH=$GUROBI_HOME/bin:/opt/local/bin\n")
    else:
        f.write("export PATH=$GUROBI_HOME/bin:/opt/local/bin:$PATH\n")

    if os.environ.get('LD_LIBRARY_PATH') is None:
        f.write("export LD_LIBRARY_PATH=$GUROBI_HOME/lib\n")
    else:
        f.write("export LD_LIBRARY_PATH=$GUROBI_HOME/lib:$LD_LIBRARY_PATH\n")

    if os.environ.get('LD_LIBRARY_PATH') is None:
        f.write("export LIBRARY_PATH=$GUROBI_HOME/lib\n")
    else:
        f.write("export LIBRARY_PATH=$GUROBI_HOME/lib:$LIBRARY_PATH\n")

    if os.environ.get('CPLUS_INCLUDE_PATH') is None:
        f.write("export CPLUS_INCLUDE_PATH=$GUROBI_HOME/include:/usr/include/python2.7\n")
    else:
        f.write("export CPLUS_INCLUDE_PATH=$GUROBI_HOME/include:/usr/include/python2.7:$CPLUS_INCLUDE_PATH\n")

