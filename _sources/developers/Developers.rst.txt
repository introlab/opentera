Developers setup guide
======================
.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: TeraServer

   Developer-Setup-for-Windows.md
   Developer-Setup-for-Mac.md
   Developer-Setup-for-Linux.md

## What you will need?
OpenTera uses cross-platform languages, allowing development to occur on multiple platform, be it Windows, Mac or Linux.

Using standard modules and technology is useful to maintain such a project over long term, but it also brings some complexity to building up a development setup. Whatever your platform of choice, you'll need the following tools:

* **A Python environment**, Python being the language used to develop the backend
  * [Miniconda](https://conda.io/miniconda.html) is used to setup the Python environment
  * [CMake](https://cmake.org/) tool is used to automate the environment building and translations management
  * [QT Creator](https://www.qt.io/product/development-tools) is recommended to simplify the build process, but not required
  * [PyCharm](https://www.jetbrains.com/pycharm/) is used as the IDE for Python, recommended, but not required as you can use any IDE you like
* **A Postgresql database**
  * [Postgresql](https://www.postgresql.org/). While OpenTera being based on [SQL Alchemy](https://www.sqlalchemy.org/) could, in theory, be used with other SQL database types (such as MySQL), the open nature of this project and of Postgresql made it the suggested database system. Thus, no support is currently explicitly provided for other databases type.
* **Redis server**
  * [Redis](https://redis.io/) is used to provide a common storage for publish/subscribe mechanism between modules and services
* **NGINX**
  * [NGINX](https://www.nginx.com/) is used to redirect requests to the appropriate service and to expose only one external port. It could also be used as a load-balancing server if required

## Specific platform setup guides

### [Developer Setup for Windows](Developer-Setup-for-Windows)
### [Developer Setup for MAC](Developer-Setup-for-Mac)
### [Developer Setup for Linux](Developer-Setup-for-Linux)
