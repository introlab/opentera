# Deploying with Docker on Linux Servers

This procedure require Linux server management knowledge and adequate permissions. It is provided as an example and can be changed according to your exact requirements and security constraints. OpenTera's authors cannot take any responsability for the use of the software, as mentioned in the [Apache Licence v2](https://www.apache.org/licenses/LICENSE-2.0.txt).

## Warnings

* If you want a test environment or a dev environment, please have a look at the [Developers Setup for Docker documentation](../dev/README.md).

## Requirements

* A Linux server installation.
* [Docker server edition](https://docs.docker.com/engine/install/) for your favorite Linux distribution.
* Make sure you setup the system with a user member of the "docker" group.
* Internet connexion

## Setup with docker-compose

[Docker Compose](https://docs.docker.com/compose/) is a tool that simplifies the management of multi-container [Docker](https://docs.docker.com/) applications. It allows you to define and run complex applications using a simple YAML file, specifying the services, networks, and volumes needed, making it easier to orchestrate and manage multiple Docker containers as a single application.

The next sections will give details of a sample docker-compose setup. Edit and change it to fit your needs.

### Installation Steps

#### Step 1: Create Docker Environment Directory

Create a directory with the name of the environment you want to configure and change directory to the newly created directory. Name the directory as you wish. All the next steps will be done in this directory.

```bash
mkdir opentera-docker-prod
cd opentera-docker-prod
```

#### Step 2: Create `docker-compose.yml` File

Create and edit a file named `docker-compose.yml` with the following [content provided here](docker-compose.yml).

#### Step 3: Create PostgreSQL Configuration file

From your base directory create a directory named `db` and a file named [init.sql](db/init.sql) that will contain all the SQL commands to initialize the databases.

#### Step 4: Create Proxy (NGINX) Configuration Files

From your base directory create a directory named `nginx` and two files named [nginx.conf](nginx/nginx.conf) and [opentera.conf](nginx/opentera.conf). The files are specifically configured to work with Docker.

> NOTE: You might have to copy manually certificates to the `certificates` shared volume.

#### Step 45: Create OpenTera Server Configuration Files

From your base directory create a directory named `teraserver` and five files named [Dockerfile](teraserver/Dockerfile), [FileTransferService.json](teraserver/FileTransferService.json), [LoggingService.json](teraserver/LoggingService.json), [TeraServerConfig.ini](teraserver/TeraServerConfig.ini) and  [VideoRehabService.json](teraserver/VideoRehabService.json).

First create the `teraserver` directory and the `Dockerfile` that will generate the teraserver image from the latest OpenTera source code from GitHub (main branch).

> Please note that this example does not provide a STUN/TURN server. Modify the file [ice_servers.json](teraserver/ice_servers.json) to configure your favorite or custom STUN/TURN servers.

### Step 6: Copy your SSL certificates to the certificates directory

The shared volume `certificates` is used to read the SSL certificate configuration.

You need the following files to match with [nginx.conf](nginx/nginx.conf) configuration :

1) certificates/site_cert.pem (main certificate)
2) certificates/site_key.pem (main certificate key)
3) certificates/ca_cert.pem (CA authority certificate, will be used to sign device certificate)

> Certificate generation / updates could be automated with a certbot or copied / linked directly to your host machine configuration.
> You can generate a local CA certificate and key with the script [CreateCertificates.py](../../teraserver/python/CreateCertificates.py)

#### Step 7: Launch the containers with Docker-Compose

Once everything is configured, launch the containers with the following command :

```bash
# This will create and download all images. This might take few minutes. After, it will launch in daemon mode.
# Docker will take care of the rest, even after reboot.
docker compose up -d
```

Congratulations, you are done!

## Backups

> Make sure you backup your configuration and your volumes regularly.

## Configure server with OpenTeraPlus

### Connecting to the Local Server with OpenTeraPlus

You can use the GUI application OpenTeraPlus to connect and configure the server. [The application can be downloaded from OpenTeraPlus files release](https://github.com/introlab/openteraplus/releases). Alternatively, you can compile the application. More information are available on [OpenTeraPlus GitHub project](https://github.com/introlab/openteraplus).

### Configuring OpenTeraPlus with your Local Server

You might want to add "opentera-docker-prod" server in the Documents/OpenTeraPlus/config/OpenTeraPlus.json for OpenTeraPlus  :

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
        "opentera-docker-prod": {
                "url": "your server name",
                "port": 40075
        }
    }
}
```

Use OpenTeraPlus to:

* Change default password for admin
* Create sites / users / participants / devices
* Configure services as needed
