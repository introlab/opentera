## Getting Started for Developers
Please follow those steps to setup your development environment. Clone this directory (change branch if not default dev) with submodules using :

```
git clone --recursive -b dev https://github.com/introlab/opentera.git
```

### Requirements
1.  Make sure you have a valid compiler installed:
    1.  Linux : gcc/g++. Install it with ```sudo apt-get install build-essential```
    2.  Mac : LLVM through XCode from the App Store
    3.  Windows: [Visual Studio C++ 2017 Community Edition](https://visualstudio.microsoft.com/fr/vs/older-downloads/)

2.  Install CMake
    1. Linux : ```sudo apt-get install cmake```
    2. Mac & Windows: Download from [here.](https://cmake.org/download/) 

3.  Install [Qt + QtCreator](https://www.qt.io/)
    1. Use the [Qt Online Installer](https://www.qt.io/download-open-source) (will require a free Qt Account)
    2. Linux: run the installer script, do not forget to make it executable first ```chmod +x <qt-unified-linux...>```
    3. Install the latest Qt Open Source Edition (Qt 5.15 Desktop or later, will be useful for Qt client application)
    4. Install all components except "Android" and "WebAssembly".
    5. Use default directories
 
4.  Install MiniConda3
    1. Use installer from [here](https://conda.io/miniconda.html)
    1. Install Python 3.x version for current user (in default user directory).
    
5.  Install [PyCharm Community Edition](https://www.jetbrains.com/pycharm/)

6.  Install PostgreSQL with default parameters
    1. Linux : ```sudo apt-get install postgresql```
    2. Mac & Windows: Download and install from : https://www.postgresql.org/download/
 
7.  Install redis server. 
    1. Recommanded: Install redis from [Docker](https://hub.docker.com/_/redis)
    2. Linux, Install redis with apt with `sudo apt-get install redis-server`
    3. Windows: install [redis binaries](https://github.com/MicrosoftArchive/redis/releases)
 
8. Install NGINX.
    1. Windows:  http://nginx.org/en/docs/windows.html
    2. Mac: install with [brew](https://brew.sh/index)
    3. Linux: install with package manager (apt)

### Step 1 : Open the root CMakeLists.txt in QtCreator
1.  Opening the root teraserver/CMakeLists.txt will allow to create and build the project
    1. Build the project **using the python-all target**, it will automatically generate the Python environment in env/python-3.6
    2. All python dependencies will be automatically downloaded
    3. Once the project is built, you will not need QtCreator (for now).
   
### Step 2 : Create a PyCharm project
1.  Using PyCharm, opening the directory "{PROJECT_ROOT}/python"
    1. Select the existing Python 3.6 environment in "{PROJECT_ROOT}/python/env/python-3.6" in the app menu: PyCharm->Preferences->Project:python->Project Interpreter
        
### Step 3 : Run the application
1.  Run the TeraServer.py application from PyCharm
2.  Edit the code as you would normally do in a python program.
3.  Run tests in the tests directory

### Notes
1.  In a near future, we hope to have everything in the QtCreator IDE. Stay tuned!

Enjoy!    
