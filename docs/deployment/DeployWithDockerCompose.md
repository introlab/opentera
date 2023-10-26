# Deploying with Docker on Linux Servers

This procedure require Linux server management knowledge and adequate permissions. It is provided as an example and can be changed according to your exact requirements and security constraints. OpenTera's authors cannot take any responsability for the use of the software, as mentioned in the [Apache Licence v2](https://www.apache.org/licenses/LICENSE-2.0.txt).

## Warnings

* If you want a test environment or a dev environment, please have a look at the [Developers Setup for Docker documentation](../developers/Developer-Setup-for-Docker).

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

Create and edit a file named `docker-compose.yml` with the following content:

```docker
version: '3.8'
#name: might not work depending on docker version, comment it to use the directory name instead (legacy)
name: opentera-docker-prod
services:
  db:
    # TODO: Use postgres latest image
    image: postgres:14.1-alpine
    restart: always
    environment:
      # TODO: Change PostGresSQL default username/password
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - db:/var/lib/postgresql/data
      # This script will initialize the DB (once) at first startup.
      - ./db/init.sql:/docker-entrypoint-initdb.d/create_tables.sql
    networks:
    # Name the network as you wish, use the same network name for all containers.
      - opentera-docker-prod-net

  cache:
    # TODO Use redis latest image
    image: redis:6.2-alpine
    restart: always
    command: redis-server --save 20 1 --loglevel warning
    volumes:
      - redis-cache:/data
    networks:
      - opentera-docker-prod-net

  proxy:
    # TODO Use nginx latest image
    image: nginx
    restart: always
    volumes:
      - ./nginx/opentera.conf:/etc/nginx/opentera.conf
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      # All your SSL certificates will need to be in the certificates volume.
      - certificates:/etc/certificates
      - nginx-logs:/etc/nginx/logs
    ports:
      # This is the port that is mapped to the outside of the container. Every traffic is routed through the reverse proxy on this port.
      - '40075:40075'
    networks:
      - opentera-docker-prod-net

  opentera-server:
    build:
      # Opentera server will be built from source inside the container with a specific Dockerfile
      dockerfile: teraserver/Dockerfile
    image: opentera-server
    restart: always
    volumes:
      - ./teraserver/TeraServerConfig.ini:/root/opentera/teraserver/python/config/TeraServerConfig.ini
      - ./teraserver/FileTransferService.json:/root/opentera/teraserver/python/services/FileTransferService/FileTransferService.json
      - ./teraserver/LoggingService.json:/root/opentera/teraserver/python/services/LoggingService/LoggingService.json
      - ./teraserver/VideoRehabService.json:/root/opentera/teraserver/python/services/VideoRehabService/VideoRehabService.json
      - files:/root/opentera/teraserver/python/services/FileTransferService/files
      - certificates:/root/opentera/teraserver/python/config/certificates
    networks:
      - opentera-docker-prod-net
    depends_on:
      - proxy
      - cache
      - db

volumes:
  db:
    driver: local

  redis-cache:
    driver: local

  certificates:
    driver: local

  nginx-logs:
    driver: local

  opentera-files:
    driver: local

networks:
  opentera-docker-prod-net:
```

#### Step 3: Create PostgreSQL Configuration file

From your base directory create a directory named `db` and a file named `init.sql` that will contain all the SQL commands to initialize the databases :

```bash
# Create directory
mkdir sql
# Use your favorite text editor to create the file.
vi sql/init.sql
```

Contents of `init.sql`:

```SQL
/* This needs to fit with OpenTera server configuration files. This script will be executed only once at first startup. */
create database opentera;
create user TeraAgent with encrypted password 'tera';
grant all privileges on database opentera to TeraAgent;
create database openteralogs;
grant all privileges on database openteralogs to TeraAgent;
create database openterafiles;
grant all privileges on database openterafiles to TeraAgent;
```

#### Step 4: Create Proxy (NGINX) Configuration Files

From your base directory create a directory named `nginx` and two files named `nginx.conf` and `opentera.conf`.

```bash
# Create directory
mkdir nginx
# Use your favorite text editor to create the file.
vi nginx/nginx.conf
```

Contents of `nginx.conf` file:

```nginx
#user  nobody;
worker_processes  1;

error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  debug;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    default_type  application/octet-stream;
    #resolver 127.0.0.1;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    # set client body size to 100M #
    client_max_body_size 100M;

    #gzip  on;
    server {
        listen       40075 ssl;
        # Setup your server name here!
        server_name  127.0.0.1;

        # Certificates need to be present!
        ssl_certificate     ../certificates/site_cert.pem;
        ssl_certificate_key  ../certificates/site_key.pem;
        ssl_client_certificate ../certificates/ca_cert.pem;

        # Redirect http to https
        error_page 497 =301 https://$host:$server_port$request_uri;

        ssl_verify_client optional;
        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;
        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers  on;

        # OpenTera configuration need to fit service configurations.
        include opentera.conf;
    }
}
```

```bash
# Use your favorite text editor to create the file.
vi nginx/opentera.conf
```

Contents of `opentera.conf` file:

```nginx
location / {
    resolver 127.0.0.11;
    proxy_pass http://opentera-server:4040;
    proxy_set_header    X-ExternalPort      $server_port;
    proxy_set_header    X-ExternalHost      $host;
    proxy_set_header    X_ExternalServer    $server_name;
    proxy_set_header    Host                $host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    X-Scheme            $scheme;
    proxy_set_header    X-Script-Name       /;
    proxy_set_header    X-SSL-CERT          $ssl_client_cert;
    proxy_set_header    X-SSL-VERIFIED      $ssl_client_verify;
    proxy_set_header    X-SSL-CLIENT-DN     $ssl_client_s_dn;
    proxy_set_header    X-SSL-ISSUER-DN     $ssl_client_i_dn;
}

location /wss {
    resolver 127.0.0.11;
    proxy_read_timeout 30s;
    proxy_pass http://opentera-server:4040/wss;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

location /log/ {
    resolver 127.0.0.11;
    proxy_pass          http://opentera-server:4041/;
    proxy_redirect      http://$host/  https://$host:$server_port/;
    proxy_set_header    X-ExternalPort      $server_port;
    proxy_set_header    X-ExternalHost      $host;
    proxy_set_header    X_ExternalServer    $server_name;
    proxy_set_header    Host                $host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    X-Scheme            $scheme;
    proxy_set_header    X-Script-Name       /log;
}

location /file/ {
    resolver 127.0.0.11;
    client_max_body_size 500M;
    proxy_pass          http://opentera-server:4042/;
    proxy_redirect      http://$host/  https://$host:$server_port/;
    proxy_set_header    X-ExternalPort      $server_port;
    proxy_set_header    X-ExternalHost      $host;
    proxy_set_header    X_ExternalServer    $server_name;
    proxy_set_header    Host                $host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    X-Scheme            $scheme;
    proxy_set_header    X-Script-Name       /file;
}

location /rehab/ {
    resolver 127.0.0.11;
    proxy_pass          http://opentera-server:4070/;
    proxy_redirect      http://$host/ https://$host:$server_port/;
    proxy_set_header    X-ExternalPort      $server_port;
    proxy_set_header    X-ExternalHost      $host;
    proxy_set_header    X_ExternalServer    $server_name;
    proxy_set_header    Host                $host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    X-Scheme            $scheme;
    proxy_set_header    X-Script-Name       /rehab;
}

########################################################################################################################
# webrtc on port xxxx
########################################################################################################################
location ~ ^/webrtc/([0-9]+)/(.*)$ {
    resolver 127.0.0.11;
    proxy_pass http://opentera-server:$1/$2$is_args$args;
    proxy_set_header    X-ExternalPort      $server_port;
    proxy_set_header    X-ExternalHost      $host;
    proxy_set_header    X_ExternalServer    $server_name;
    proxy_set_header    Host                $host;
    proxy_set_header    X-Real-IP           $remote_addr;
    proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto   $scheme;
    proxy_set_header    X-Scheme            $scheme;
    proxy_set_header    X-Script-Name       /webrtc/;
}

location ~ ^/websocket/([0-9]+)/(.*)$ {
    resolver 127.0.0.11;
    proxy_pass http://opentera-server:$1/websocket/$1/$2$is_args$args;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

#### Step 4: Create OpenTera Server Configuration Files

From your base directory create a directory named `teraserver` and five files named `Dockerfile`, `FileTransferService.json`, `LoggingService.json`, `TeraServerConfig.ini` and  `VideoRehabService.json`.

First create the `teraserver` directory and the `Dockerfile` that will generate the teraserver image from the latest OpenTera source code from GitHub (main branch).

```bash
mkdir teraserver
vi teraserver/Dockerfile
```

Contents of `Dockerfile` file:

```Docker
FROM ubuntu:22.04

# Change default shell to bash
SHELL ["/bin/bash", "-c"]

# Install build dependencies
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
	build-essential cmake git sudo vim libprotobuf-dev protobuf-compiler locales wget curl

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install miniconda
WORKDIR /root
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Install latest npm / nodejs
RUN curl -sL https://deb.nodesource.com/setup_18.x -o nodesource_setup.sh
RUN bash ~/nodesource_setup.sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# Clone OpenTera code
WORKDIR /root
RUN ["/bin/bash", "-c", "git clone -b main https://github.com/introlab/opentera.git --recurse-submodules"]

# Install node-js signaling server
WORKDIR /root/opentera/teraserver/easyrtc
RUN ["/bin/bash", "-c", "npm install"]

# Build environment
WORKDIR /root/opentera/teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make python-all"]

ENV PYTHON3_EXEC /root/opentera/teraserver/python/env/python-3.11/bin/python3

# Set Python path
ENV PYTHONPATH /root/opentera/teraserver/python

# RUN SERVER
WORKDIR /root/opentera/teraserver/python

# RUN TERA SERVER
CMD ["/bin/bash", "-c", "$PYTHON3_EXEC TeraServer.py"]
```

Then create and edit the other configuration files :

```bash
vi teraserver/FileTransferService.json
vi teraserver/LoggingService.json
vi teraserver/TeraServerConfig.ini
vi teraserver/VideoRehabService.json
```

Contents of `FileTransferService.json`:

```json
{
    "Service": {
      "name": "FileTransferService",
      "hostname": "127.0.0.1",
      "port": 4042,
      "debug_mode": false
    },
    "Backend": {
      "hostname": "proxy",
      "port": 40075
    },
    "Redis": {
      "hostname": "cache",
      "port": 6379,
      "db": 0,
      "username": "",
      "password": ""
    },
    "FileTransfer" : {
      "files_directory": "files"
    },
    "Database": {
      "db_type": "QPSQL",
      "name": "openterafiles",
      "url": "db",
      "port": 5432,
      "username": "teraagent",
      "password": "tera"
    }
  }
````

Contents of `LoggingService.json`:

```json
{
    "Service": {
      "name": "LoggingService",
      "hostname": "127.0.0.1",
      "port": 4041,
      "debug_mode": false
    },
    "Backend": {
      "hostname": "proxy",
      "port": 40075
    },
    "Redis": {
      "hostname": "cache",
      "port": 6379,
      "db": 0,
      "username": "",
      "password": ""
    },
    "Logging" : {
      "level": "trace"
    },
    "Database": {
      "db_type": "QPSQL",
      "name": "openteralogs",
      "url": "db",
      "port": 5432,
      "username": "teraagent",
      "password": "tera"
    }
  }
````

Contents of `TeraServerConfig.ini`:

```json
{
    "Server": {
        "name": "Docker Server",
        "hostname": "127.0.0.1",
        "port": 4040,
        "use_ssl": false,
        "ssl_path": "config/certificates",
        "site_certificate": "site_cert.pem",
        "site_private_key": "site_key.pem",
        "ca_certificate": "ca_cert.pem",
        "ca_private_key": "ca_key.pem",
        "upload_path": "uploads",
        "debug_mode": true,
        "enable_docs": true
    },
    "Database": {
        "db_type": "QPSQL",
        "name": "opentera",
        "url": "db",
        "port": 5432,
        "username": "teraagent",
        "password": "tera"
    },
    "Redis": {
        "hostname": "cache",
        "port": 6379,
        "db": 0,
        "username": "",
        "password": ""
    }
}
````

Contents of `VideoRehabService.json`:

```json
{
    "Service": {
        "name": "VideoRehabService",
        "hostname": "127.0.0.1",
        "port": 4070,
        "debug_mode": false
    },
    "Backend": {
        "hostname": "proxy",
        "port": 40075
    },
    "Redis": {
        "hostname": "cache",
        "port": 6379,
        "db": 0,
        "username": "",
        "password": ""
    },
    "WebRTC": {
        "hostname": "127.0.0.1",
        "external_port": 40075,
        "local_base_port": 8080,
        "max_sessions": 50,
        "working_directory": "../../../easyrtc",
        "executable": "node",
        "script": "server.js"
    }
}
````

#### Step 5: Launch the containers with Docker-Compose

Once everything is configured, launch the containers with the following command :

```bash
# This will create and download all images. This might take few minutes. After, it will launch in daemon mode.
# Docker will take care of the rest, even after reboot.
docker compose up -d
```

Congratulations, you are done!

## Backups

>Make sure you backup your configuration and your volumes regularly.

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
