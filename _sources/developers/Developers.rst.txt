Developers setup guide
======================
OpenTera uses cross-platform languages, allowing development to occur on multiple platform, be it Windows, Mac or Linux.

Using standard modules and technology is useful to maintain such a project over long term, but it also brings some complexity to building up a development setup. Whatever your platform of choice, you'll need the following tools:

* **A Python environment**, Python being the language used to develop the backend
  * `Miniconda <https://conda.io/miniconda.html>`_ is used to setup the Python environment
  * `CMake <https://cmake.org/>`_ tool is used to automate the environment building and translations management
  * `QT Creator <https://www.qt.io/product/development-tools>`_ is recommended to simplify the build process especially on Windows, but not required
  * `PyCharm <https://www.jetbrains.com/pycharm/>`_ is used as the IDE for Python, recommended, but not required as you can use any IDE you like
* **A Postgresql database**
  * `Postgresql <https://www.postgresql.org/>`_. While OpenTera being based on `SQL Alchemy <https://www.sqlalchemy.org/>`_ could, in theory, be used with other SQL database types (such as MySQL), the open nature of this project and of Postgresql made it the suggested database system. Thus, no support is currently explicitly provided for other databases type.
* **Redis server**
  * `Redis <https://redis.io/>`_ is used to provide a common storage for publish/subscribe mechanism between modules and services
* **NGINX**
  * `NGINX <https://www.nginx.com/>`_ is used to redirect requests to the appropriate service and to expose only one external port. It could also be used as a load-balancing server if required

See the following sections for platform specific instructions:

.. toctree::
   :maxdepth: 1

   Developer-Setup-for-Windows.md
   Developer-Setup-for-Mac.md
   Developer-Setup-for-Linux.md
