# Deploying OpenTera on a server

Those setup instructions suppose a pre-installed and configured Ubuntu 20.04 server installation, either in a virtual machine or on a physical machine.

## Pre-requisites

This section configures the depending packages and software before installing the main OpenTera server.

***

### Postgresql

***

1. Install Postgresql package: `sudo apt-get install postgresql`
2. Change default `postgres` user password for a more secure installation: 
    ```
    sudo -u postgres psql
    ALTER USER postgres PASSWORD 'TypeThePasswordHere';
    ```
3. (Optional) Setup a local pgAdmin instance to connect to postgresql database (optionally using a SSH tunnel)
4. Create `teraagent` user in database (or name of your choice, but will have to be adjusted in the config section below):
    ```
    CREATE USER teraagent WITH ENCRYPTED PASSWORD 'TypeUserPasswordHere';
    ```
5. Create required database and assign `teraagent` user to them:
    ```    
    CREATE DATABASE opentera WITH OWNER=teraagent;
    CREATE DATABASE openterafiles WITH OWNER=teraagent;
    CREATE DATABASE openteralogs WITH OWNER=teraagent;
    ```
6. Don't forget to quit the postgres console: `\q`

***
### Redis
***

1. Install redis server: `sudo apt-get install redis-server`
2. (Optional, but strongly recommended) Setup a password to the redis server instance: 
    ```
    `sudo nano /etc/redis/redis.conf`
    Edit the line `requirepass` and set your password
    Save, close and restart the redis server: `sudo systemctl restart redis.service`
    ```

***
### nginx
***
Only basic configuration is done here - specific OpenTera configuration is done below

1. Install nginx: `sudo apt-get install nginx`

***
### Python environment (using miniconda)
***
1. Follow the instructions [here­](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) to download and install miniconda
2. When requested, execute the `conda init` command
3. Close your shell and restart it again

***
### Build environment
***
1. Install git: `sudo apt-get install git`
2. Install cmake: `sudo apt-get install cmake`
3. Install g++: `sudo apt-get install g++`
4. Install nodejs / npm: `sudo apt-get install npm`

***
## OpenTera installation

This section proceeds to the installation of the OpenTera server

***
### Installation
***
1. Fetch the OpenTera code with submodules using git: `git clone --recurse-submodules https://github.com/introlab/opentera.git`
2. `cd opentera/teraserver` (or the location that you cloned the project)
3. Initialize cmake environment: `cmake .`
4. Generate python environment using make: `make python-all`
5. Generate nodejs environment for VideoRehab service:
    ```
    cd opentera/teraserver/easyrtc
    npm install
    ```

***
### Configuration
***
#### Config files
There is a few config files to edit. You should edit each of them and put the correct parameters, according to your setup and the passwords you've set previously. Here is the list of the files:

* `teraserver/python/config/TeraServerConfig.ini`: the main config file. "port" and "hostname" shouldn't be changed.
* `teraserver/python/config/nginx.conf`: nginx config file. Unless listening to a different port and setting correct ssl certificates, nothing should be changed in that file.
* `teraserver/python/services/FileTransferService/FileTransferService.json`: the file transfer service configuration.
* `teraserver/python/services/LoggingService/LoggingService.json`: the logging service configuration.
* `teraserver/python/services/VideoRehabService/VideoRehabService.json`: make sure to set the "WebRTC - hostname" value to the external server address.

#### nginx configuration
1. Create nginx configuration file: `sudo nano /etc/nginx/sites-available/opentera`
2. Copy the `server` section (only) from the `teraserver/python/config/nginx.conf` file. 
3. Edit the `ssl_certificate`, `ssl_certificate_key`, `ssl_client_certificate` to point to your correct SSL setup.
4. Edit the `include opentera.conf` line with the full path to the `opentera.conf` file, for example: `/home/baseuser/opentera/teraserver/python/config/opentera.conf;`
5. Enable the site by creating a symbolic link into the sites-enabled folder: `sudo ln -s /etc/nginx/sites-available/opentera /etc/nginx/sites-enabled/`

6. Restart the nginx server: `sudo systemctl restart nginx`

#### Service configuration
TO ensure that OpenTera will run automatically and after a reboot, a systemd service can be created. 

1. Create the `/lib/systemd/system/opentera.service` file with the following content:
```
[Unit]
Description=OpenTeraServer
After=network-online.target

[Service]
User=**PUT THE EXECUTING USER HERE**
Group=**PUT THE EXECUTING GROUP HERE**
Environment=PYTHONPATH=**(path to opentera)**/opentera/teraserver/python
ExecStart=**(path to opentera)**/opentera/teraserver/python/env/python-3.8/bin/python3 **(path to opentera)**/opentera/teraserver/python/TeraServer.py
WorkingDirectory=**(path to opentera)**/opentera/teraserver/python
StandardOutput=syslog+console
StandardError=syslog+console
Restart=always
RestartSec=10s
KillMode=process
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target

```
2. Enable service: `sudo systemctl enable opentera.service`
3. Start service: `sudo systemctl start opentera.service`

***
## Post installation
Optional post installation steps.

***
### Local TURN/STUN server
***
TODO. coturn setup instructions.

***
### SSL certificate with LetsEncrypt
***
1. Install certbot agent: `sudo apt-get install certbot`
2. Install nginx plugin: `sudo apt-get install python3-certbot-nginx`
3. Run certbot: `sudo certbot --nginx -d (your_host_name)`

