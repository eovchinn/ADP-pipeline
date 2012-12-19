Installation on Linux (tested on Ubuntu64)
=========================================

#### Go to scripts-linux directory.

```
cd scripts-linux
```

#### Change permission on .sh files:

```
chmod 755 *.sh
```

#### Install pre-requisites. This requires ROOT permission.

```
sudo ./install-prereq-linux.sh
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

* Linux32: `deploy-all-linux32.sh`
* Linux64: `deploy-all-linux64.sh`

```
./deploy-all-linux64.sh installation_directory gurobi_file_location gurobi_license_key boxer_username boxer_password boxer_models_file_location
```

   * installation_directory: this is the directory where the package will be installed. Should be in a location where you have write permission (e.g. /home/me/adp_home)
   * gurobi_file_location: full path for gurobi package downloaded in step 3 (e.g., /home/me/package/gurobi5.0.1_linux64.tar.gz)
   * gurobi_license_key: license key generated in step 3.
   * boxer_username: username for boxer website (step 4) 
   * boxer_password: password for boxer website (step 4)
   * boxer_models_file_location: models downloaded in step 4 (e.g.,/home/me/package/models-1.02.tgz)

>"NOTE: You will be asked to specify a location for the GUROBI license
file. When asked, enter the same location as the
installation_directory. If you choose a different location you have to
modify GRB_LICENSE_FILE in the environment to reflect this."

#### Test your installation.

* Linux32: `./test_install32.sh installation-directory`
* Linux64: `./test_install64.sh installation-directory`

#### Set permanant environment variables. 

>"This step will modify your
.bashrc file!!! You can either run the script to set your environment variables
in .bashrc, or you can set them manually."

* Linux32: `python setenv-linux32.py installation-directory`
* Linux64: `python setenv-linux64.py installation-directory`

   * installation_directory: this is the directory where the package has been installed. Should be the same as the installation-directory provided above.
