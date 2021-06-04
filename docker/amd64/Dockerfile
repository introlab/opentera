# Image: introlab3it/openteraserver
# LABEL version="1.0.6"
# LABEL description="OpenTera Test Server from IntRoLab."

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake git sudo vim libprotobuf-dev \
	cmake protobuf-compiler locales wget curl nginx

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Clone repository
# ARG CACHE_DATE=2021-06-04
RUN git clone --recurse-submodules -b main https://github.com/introlab/opentera.git

#Create dbs and users
RUN service postgresql start &&\
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'opentera';"&&\
	sudo -u postgres psql -c "create database opentera" &&\
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"&&\
	sudo -u postgres psql -c "grant all privileges on database opentera to TeraAgent;"&&\
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"&&\
	sudo -u postgres psql -c "create database openteralogs" &&\
	sudo -u postgres psql -c "grant all privileges on database openteralogs to TeraAgent;"&&\
	sudo -u postgres psql -c "create database openterafiles" &&\
	sudo -u postgres psql -c "grant all privileges on database openterafiles to TeraAgent;"&&\
	sudo -u postgres psql -c "\l"

#VOLUMES
RUN mkdir /config
VOLUME /config
VOLUME /var/lib/postgresql


# Install miniconda
WORKDIR /root
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Install latest npm / nodejs
RUN curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
RUN bash ~/nodesource_setup.sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# Build environment
WORKDIR /opentera/teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make python-all"]

ENV PYTHON3_EXEC /opentera/teraserver/python/env/python-3.8/bin/python3

# Install nodejs package
WORKDIR /opentera/teraserver/easyrtc
RUN npm install

# Final working directory
WORKDIR /opentera/teraserver/python

# Create certificates from new python env
RUN ["/bin/bash", "-c", "$PYTHON3_EXEC ./CreateCertificates.py"]
RUN ["/bin/bash", "-c", "ls -l certificates/"]
VOLUME /opentera/teraserver/python/certificates

# Private and public mapping
# NGINX
EXPOSE 40075/tcp
# REDIS
EXPOSE 6379/tcp
# POSTGRESQL
EXPOSE 5432/tcp

# env with a default value
ENV OPENTERA_CONFIG_PATH /opentera/teraserver/python/config/TeraServerConfig.ini

# Create nginx logs directory
RUN mkdir -p config/logs
# Set Python path
ENV PYTHONPATH /opentera/teraserver/python

# Run the required services and python script
CMD nginx -c /opentera/teraserver/python/config/nginx.conf -p /opentera/teraserver/python/config/ && ./start_docker.sh
