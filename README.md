# pykeycollect 
* A python framework for collecting keystroke biometrics

# Available Features

* Tri-Graph Hold Times - This is the hold time of a given key when preceeded by one key and followed by another
* Full KeyStroke Log

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


# Running the Logger
If you built the executeable, simply run the output file in the dist folder to start the logging process. Alternatively you can run the script directly as 
```
(keys_build) ~/pykeycollect> python Collector.py
```

Depending on your security policies you may need to run the executable as an administrator (sudo) for it to capture keyboard events. 

If running on OSX you may get the following error message upon start
```
... is calling TIS/TSM in non-main thread environment, ERROR : This is NOT allowed. Please call TIS/TSM in main thread!!!
```

This can be safely ignored for the time being, it is a known bug but it does not interfere with keystroke collection.

## Tray Icon
Once the logger is started, a tray icon with a green/black checkered icon will show up in your system tray (windows) or in the upper left corner status tray (OSX). Clicking this icon (right click on windows) will bring up a context menu which allows you to enable/disable the logger, or close the logger altogether. 

## Output file
The current HEAD version of the repo has only the full keystroke logger enabled. This will generate a csv file with the following structure:
```
ScanCode, KeyName, Action, Time
```

* Scancode is the code returned by the operating system
* KeyName is the name of the key
* Action is U or D for up or down
* Time is the micro-second resolution result of time.perf_counter() indicating the time since the app started when the keystroke event occured.
