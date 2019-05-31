# Image: introlab3it/openteraserver

# LABEL version="0.1"
# LABEL description="OpenTera Test Server from IntRoLab."

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake python3.6 git \
        python3-pip sudo vim libprotobuf-dev cmake protobuf-compiler

# Clone repository
ARG CACHE_DATE=2019-05-31
RUN git clone -b dev https://github.com/introlab/opentera.git

#Create db and user
RUN service postgresql start &&\
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'test';"&&\
	sudo -u postgres psql -c "create database test" &&\
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"&&\
	sudo -u postgres psql -c "grant all privileges on database test to TeraAgent;"&&\
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"&&\
	sudo -u postgres psql -c "\l"

#VOLUME
RUN mkdir /config
VOLUME /config

# Install python dependencies, must be installed before we run cmake
WORKDIR /opentera/teraserver/python/env

# protobuf is the only one not in the requirements file
RUN pip3 install protobuf
RUN pip3 install -r requirements.txt


# Everything else is automated with cmake
WORKDIR /opentera/teraserver
RUN cmake .
RUN make docker-all

# Final working directory
WORKDIR /opentera/teraserver/python

# Private and public mapping
EXPOSE 4040/tcp



# env with a default value
ENV OPENTERA_CONFIG_PATH /opentera/teraserver/config/TeraServerConfig.ini

# Run the required services and python script
CMD ls -l && ./start.sh



