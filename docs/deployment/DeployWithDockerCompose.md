# Deploying with Docker Compose on Windows/Mac/Linux

[Docker Compose](https://docs.docker.com/compose/) is a tool that simplifies the management of multi-container [Docker](https://docs.docker.com/) applications. It allows you to define and run complex applications using a simple YAML file, specifying the services, networks, and volumes needed, making it easier to orchestrate and manage multiple Docker containers as a single application. An example Docker Compose configuration is provided with OpenTeraServer on GitHub in the [docker/dev](https://github.com/introlab/opentera/tree/main/docker/dev) directory.

## Warnings

The following example is provided for testing on a local machine and is not suited for production.

## Requirements

* [Install Docker Desktop for Windows/Linux/Mac](https://www.docker.com/products/docker-desktop/)
* [Install Visual Studio Code](https://code.visualstudio.com/download)
* Enough free space on your disk (10Gb+)

### Install Docker Desktop

* Follow installation procedures for your operating system and use default settings. You might need to have Administration rights to proceed with installation.

### Install Visual Studio Code

* Follow installation procedures for your operating system and use default settings. You might need to have Administration rights to proceed with installation.

#### Visual Studio Code Extensions

Launch Visual Studio Code and install the following [extensions](https://code.visualstudio.com/docs/editor/extension-marketplace):

* [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
* [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
* [CMake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake)
* [Markdown](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)

## Open OpenTera Base Folder in Visual Studio Code

We assume here that you have cloned the [code from GitHub](https://github.com/introlab/opentera.git).
You must select the root directory of the opentera git project.

### Build the Development Environment with docker-compose

A sample [docker-compose.yml](https://github.com/introlab/opentera/blob/main/docker/dev/docker-compose.yml) file is provided that generates a full environment with the following components running in individual containers :

* Redis server
* PostgresSQL server
* NGINX reverse proxy server
* A certificate generator for https self-signed certificates
* TeraServer and base services

Procedure:

1. Right-click on the [docker-compose.yml](https://github.com/introlab/opentera/blob/main/docker/dev/docker-compose.yml) and select "Compose Up". This can take several minutes the first time to download all the images and start the containers.
2. Docker compose will create **volumes** (shared disks) to store your databases, configurations, files as specified in the "volume:" section. Those directories are automatically mounted when the containers are started.
3. When running for the first time, databases with default values are generated.
4. **The default user is "admin" with password "admin".**
5. The opentera source code is copied (not mounted) at the moment. If you make changes in the code, you need to do "Compose Up" again to generate the new container.

**At this stage you have a running OpenTeraServer on your local machine on port 40075. Congratulations!**

API Documentation can be viewed by browsing to [https://localhost:40075/doc](https://localhost:40075/doc). Accept the security risks if your browser is giving you a warning, this is caused because by your local server using a self generated certificate.

### Connecting to the Local Server with OpenTeraPlus

You can use the GUI application OpenTeraPlus to connect and configure the server. [The application can be downloaded from OpenTeraPlus files release](https://github.com/introlab/openteraplus/releases). Alternatively, you can compile the application. More information are available on [OpenTeraPlus GitHub project](https://github.com/introlab/openteraplus).

#### Configuring OpenTeraPlus with your Local Server

The default OpenTeraPlus configuration should allow you to connect to the server named: "Local - Port 40075". You might want to add "Local-Docker" server in the Documents/OpenTeraPlus/config/OpenTeraPlus.json for OpenTeraPlus if you decide to change your docker-compose configuration with a new port :

```json
{
    "Settings": {
        "showServers": true,
        "logToFile": true
    },
    "Servers": {
        "Local - Port 40075": {
                "url": "localhost",
                "port": 40075
        },
        "Local-Docker": {
                "url": "localhost",
                "port": 40075
        }
    }
}
```

## Advanced Options

### Connect to the Local Database using pgAdmin

[pgAdmin](https://www.pgadmin.org/) is an open-source administration and management tool for the PostgreSQL database. It provides a user-friendly graphical interface for interacting with PostgreSQL databases, allowing users to perform tasks like querying the database, managing tables and data, and configuring server settings without needing to use command-line tools.

You can connect to the PostgreSQL database running in your container by using port **5433** and using **user: "postgres"** and **password: "postgres"**. This is useful for debugging databases or to understand its structure.

### Connect to Redis

Redis connexion is available on port **6380**. You can use your favorite tool to inspect the cache.

### Debugging with VS Code

Using the Visual Studio Code remote debugger, you can connect to running code in the opentera-server container on port 5678. A mapping to the local code corresponding to the container TeraServer code is required. You can create a configuration file named "launch.json" in the .vscode directory that contains :

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}${pathSeparator}teraserver${pathSeparator}python",
                    "remoteRoot": "/teraserver/python"
                }
            ],
            "justMyCode": true
        }
    ]
}

```

With this configuration, you can put breakpoints in the local python code and you will be able to inspect variables.
