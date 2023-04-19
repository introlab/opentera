# Getting Started for Developers - Docker

## Pre-requisites

* [Install Docker Desktop for Windows/Linux/Mac](https://www.docker.com/products/docker-desktop/)
* [Install Visual Studio Code](https://code.visualstudio.com/download)
* Enough free space on your disk (10Gb+)

### Install Docker Desktop

* Follow installation procedures and use default settings.

### Install Visual Studio Code

* Follow installation procedures and use default settings.

#### Visual Studio Code Extensions

* Install the following extensions:
  * [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  * [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  * [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
  * [CMake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake)
  * [Markdown](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)

## Open OpenTera Base Folder in Visual Studio Code

You must select the root directory of the opentera git project.

## Build the Development Environment with docker-compose

A sample [docker-compose.yml](./docker-compose.yml) file is provided that generates a full environment with the following components running in individual containers :
- Redis server
- PostgresSQL server 
- NGINX reverse proxy server 
- A certificate generator for https self-signed certificates
- TeraServer and base services

>1. Right-click on the [docker-compose.yml](./docker-compose.yml) and select "Compose Up". This can take several minutes the first time to download all the images and start the containers.

>2. Docker compose will create **volumes** (shared disks) to store your databases, configurations, files as specified in the "volume:" section. Those directories are automatically mounted when the containers are started. 

>3. When running for the first time, databases with default values are generated.

>4. The default user is "admin" with password "admin".

>5. The opentera source code is copied (not mounted) at the moment. If you make changes in the code, you need to do "Compose Up" again to generate the new container.

## Debugging with VS Code

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
