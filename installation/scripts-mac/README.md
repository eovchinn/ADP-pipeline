Installation on MAC (tested on 10.7)
=========================================

#### Before you Start

* Install MacPorts. MacPorts is used to install all "helper" packages.
```
http://www.macports.org
```

#### Go to scripts-mac directory.

```
cd scripts-mac
```

#### Change permission on .sh files:

```
chmod 755 *.sh
```

#### Install pre-requisites (with MacPorts). 

This requires ROOT permission.

```
sudo ./install-prereq-mac.sh
```

#### Register on GUROBI website and download gurobi package.

```
http://www.gurobi.com
```

*  Go to Download/Gurobi Optimizer and download package appropriate for
you environment.

* Go to Download/License and get a Gurobi license key. SAVE THE KEY IN A
SAFE PLACE.

#### Register on BOXER website.

```
http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer
```

* Go to Download page and download "models trained on CCGbank 02-21 and
MUC 7" in "gzipped tar" format. 


#### Install ADP package.

<"you will be asked for password as GUROBI
installation requires root permissions"

```
./deploy-all-mac.sh installation_directory gurobi_file_location gurobi_license_key boxer_username boxer_password boxer_models_file_location
```

    * installation_directory: this is the directory where the package will be installed. Should be in a location where you have write permission (e.g. /home/me/adp_home)
    * gurobi_file_location: full path for gurobi package downloaded in step 3 (e.g., /home/me/package/gurobi5.0.1_mac64.pkg)
    * gurobi_license_key: license key generated in step 3.
    * boxer_username: username for boxer website (step 4) 
    * boxer_password: password for boxer website (step 4)
    * boxer_models_file_location: models downloaded in step 4 (e.g.,/home/me/package/models-1.02.tgz)

>"NOTE: You will be asked to specify a location for the GUROBI license
file. When asked, enter the same location as the
installation_directory. If you choose a different location you have to
modify GRB_LICENSE_FILE in the environment to reflect this."

#### Test your installation.

`./test_install-mac.sh installation-directory`

#### Set permanant environment variables. 

>"This step will modify your
.bash_profile file!!! You can either run the script to set your
environment variables in .bash_profile, or you can set them manually."

`python setenv-mac.py installation-directory`

    * installation_directory: this is the directory where the package has been installed. Should be the same as the installation-directory provided above.
