# Code structure
The OpenTera project is logically organized into folders based on the [architecture](Architecture-Overview) of the platform.

## Root
At the root of the project:
* **[`docker`](https://github.com/introlab/opentera/tree/main/docker)** containing the [docker](https://www.docker.com/) files used to [deploy in a docker environment](Deployment)
* **[`teraserver`](https://github.com/introlab/opentera/tree/main/teraserver)** containing the OpenTera source files

## [Source folder](https://github.com/introlab/opentera/tree/main/teraserver)
The base source folder contains the following folders:
* **[`docs`](https://github.com/introlab/opentera/tree/main/teraserver/docs)** containing the current database graph and other more dynamic documentation elements not covered in this wiki
* **[`easyrtc`](https://github.com/introlab/opentera/tree/main/teraserver/easyrtc)** containing the [video rehab service](Videorehab-Service) web files used by the WebRTC subsystem
* **[`linux`](https://github.com/introlab/opentera/tree/main/teraserver/linux)** containing sample services files to be used when [deploying on a server](Deployment)
* **[`python`](https://github.com/introlab/opentera/tree/main/teraserver/python)** containing the main OpenTera source code (see below)

### [OpenTera source code structure](TeraServer-Service)
* **[`alembic`](https://github.com/introlab/opentera/tree/main/teraserver/python/alembic)** containing the [Alembic](https://alembic.sqlalchemy.org) versions used when upgrading the [database structure](Database-Structure)
* **[`certificates`](https://github.com/introlab/opentera/tree/main/teraserver/python/certificates)** used to store signing certificates for devices and, optionally, external certificates used by NGINX
* **[`config`](https://github.com/introlab/opentera/tree/main/teraserver/python/config)** containing the NGINX config files
* **[`docker`](https://github.com/introlab/opentera/tree/main/docker)** containing the [docker](https://www.docker.com/) files used to [deploy in a docker environment](Deployment)
* **[`env`](https://github.com/introlab/opentera/tree/main/teraserver/python/env)** containing the `requirements.txt` file used to [generate the python environment](Developers). Will also holds the generated environment.
* **[`examples`](https://github.com/introlab/opentera/tree/main/teraserver/python/examples)** containing some python client examples
* **[`modules`](https://github.com/introlab/opentera/tree/main/teraserver/python/modules)** containing the source codes of each of the [various modules part of the OpenTera platform](Architecture-Overview).
* **[`opentera`](https://github.com/introlab/opentera/tree/main/teraserver/python/opentera)** containing the common classes that can be needed for the various [services](Architecture-Overview) and useful when [creating new services](Service-Creation). This folder contains the [database models](Database-Structure), the [internal communication module](Internal-services-communication-module) and the [communication messages structure](Messages-structure).
* **[`services`](https://github.com/introlab/opentera/tree/main/teraserver/python/services)** containing the various [system services](Architecture-Overview) of the OpenTera platform.
* **[`static`](https://github.com/introlab/opentera/tree/main/teraserver/python/static) and [`templates`](https://github.com/introlab/opentera/tree/main/teraserver/python/templates)** containing the static assets and templates to display the server information page ("about") and [API](API) documentation page.
* **[`tests`](https://github.com/introlab/opentera/tree/main/teraserver/python/tests)** containing the [unit tests](Running-tests) used in the development process.
* **[`tools`](https://github.com/introlab/opentera/tree/main/teraserver/python/tools)** containing stand-alone scripts that can be used as various tools (such as importing data from another system)
* **[`translations`](https://github.com/introlab/opentera/tree/main/teraserver/python/translations)** containing the [translations files](Translations) of the system
