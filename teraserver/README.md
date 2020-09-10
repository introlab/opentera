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
    3. Install the latest Qt Open Source Edition (Qt 5.14.2 Desktop or later, will be useful for Qt client application)
    4. Install all components except "Android" and "WebAssembly".
    5. Use default directories
 
4.  Install MiniConda3
    1. Use installer from [here](https://conda.io/miniconda.html)
    2. Install Python 3.x version for current user (in default user directory).
    3. Use default settings.
    
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
    3. Linux: install with package manager : ```sudo apt-get install nginx```

### Step1 : Create the database and database users (only once)
This step needs to be done only once.
   ```
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'test';"
	sudo -u postgres psql -c "create database test;" 
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"
	sudo -u postgres psql -c "grant all privileges on database test to TeraAgent;"
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"
	sudo -u postgres psql -c "create database openteralogs;"
	sudo -u postgres psql -c "grant all privileges on database openteralogs to TeraAgent;"
	sudo -u postgres psql -c "create database openterafiles;"
	sudo -u postgres psql -c "grant all privileges on database openterafiles to TeraAgent;"
	sudo -u postgres psql -c "create database videodispatch;"
	sudo -u postgres psql -c "create user videodispatch with encrypted password 'videodispatch';"
	sudo -u postgres psql -c "grant all privileges on database videodispatch to videodispatch;"
	sudo -u postgres psql -c "ALTER USER videodispatch WITH PASSWORD 'videodispatch';"
	sudo -u postgres psql -c "create database bureauactif;"
	sudo -u postgres psql -c "create user bureauactif with encrypted password 'bureauactif';"
	sudo -u postgres psql -c "grant all privileges on database bureauactif to bureauactif;"
	sudo -u postgres psql -c "ALTER USER bureauactif WITH PASSWORD 'bureauactif';"
	sudo -u postgres psql -c "\l"
   ```
### Step 2 : Open the root CMakeLists.txt in QtCreator (only once)
1.  Opening the root teraserver/CMakeLists.txt will allow to create and build the project
    1. Build the project **using the python-all target**, it will automatically generate the Python environment in env/python-3.6
    2. Click on the "Projects" and change Build steps target by clicking on "Details"
    2. All python dependencies will be automatically downloaded
    3. Once the project is built, you will not need QtCreator (for now).
   
### Step 3 : Create a PyCharm project (only once)
1.  Using PyCharm, opening the directory "{PROJECT_ROOT}/python"
    1. Select the existing Python 3.6 environment in "{PROJECT_ROOT}/python/env/python-3.6" in the app menu: PyCharm->Preferences->Project:python->Project Interpreter
        
### Step 4: Generate the TLS certicates (only once)
1. Using PyCharm, run the CreateCretificates.py script. This will generate the TLS certificates used by nginx.

### Step 5 : Run the nginx reverse proxy (every time)
1. Go to the **{PROJECT_ROOT}/teraserver/python/config** directory.
2. Create the logs directory (only once) : ```mkdir logs```
3. Run the script : ```./start_nginx.sh```

### Step 6 : Run the application (every time)
1.  Run the TeraServer.py application from PyCharm
2.  Edit the code as you would normally do in a python program.
3.  Run tests in the tests directory

### Step 7 : Try the API with swagger UI" (as needed)
1. Navigate to : [API](https://localhost:40075/doc)

### Notes
1.  In a near future, we hope to have everything in the QtCreator IDE. Stay tuned!

Enjoy!    
