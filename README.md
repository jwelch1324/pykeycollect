# pykeycollect 
* A python framework for collecting keystroke biometrics

# Available Features

* Tri-Graph Hold Times - This is the hold time of a given key when preceeded by one key and followed by another


# Requirements
* Conda or MiniConda
* Python 3+
* https://github.com/boppreh/keyboard -- Installed by conda environment, see below

# Setting up the Environment and Building the Executable
Included in the repo are several .yml files which specify different conda environments. It is safe to simply use the keys_win_build.yml environment for all development purposes (unless you require an MKL backed numpy), but it is necessary to use it for deployment when using pyinstaller otherwise the final executable will be 200+ MB. 

To setup the environment simply execute the following command in an anaconda prompt
## Windows
```
~/pykeycollect> conda env create -f keys_win_build.yml
```
## OSX
```
~/pykeycollect> conda env create -f keys_osx_build.yml
```

## Activate the Environment and build
After installation completes, activate the environment and run pyinstaller with the included .spec file
```
~/pykeycollect> conda activate keys_build
(keys_build) ~/pykeycollect> pyinstaller Collector.spec
```
This will build an executable called Collector.exe in the dist folder. 
