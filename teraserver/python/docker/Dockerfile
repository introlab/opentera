# Image: introlab3it/openteraserver

# LABEL version="0.1"
# LABEL description="OpenTera Test Server from IntRoLab."

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake python3.6 git python3-babel \
        python3-pip sudo vim libprotobuf-dev cmake protobuf-compiler locales wget nginx

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Clone repository
ARG CACHE_DATE=2020-04-06
RUN git clone -b dev https://github.com/introlab/opentera.git

#Create dbs and users
RUN service postgresql start &&\
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'test';"&&\
	sudo -u postgres psql -c "create database test" &&\
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"&&\
	sudo -u postgres psql -c "grant all privileges on database test to TeraAgent;"&&\
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"&&\
	sudo -u postgres psql -c "create database videodispatch" &&\
	sudo -u postgres psql -c "create user videodispatch with encrypted password 'videodispatch';"&&\
	sudo -u postgres psql -c "grant all privileges on database videodispatch to videodispatch;"&&\
	sudo -u postgres psql -c "ALTER USER videodispatch WITH PASSWORD 'videodispatch';"&&\
	sudo -u postgres psql -c "\l"

#VOLUME
RUN mkdir /config
VOLUME /config

# Install miniconda
WORKDIR /root
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Build environment
WORKDIR /opentera/teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make python-all"]

ENV PYTHON3_EXEC /opentera/teraserver/python/env/python-3.6/bin/python3

# Final working directory
WORKDIR /opentera/teraserver/python

# Create certificates from new python env
RUN ["/bin/bash", "-c", "$PYTHON3_EXEC ./CreateCertificates.py"]
RUN ["/bin/bash", "-c", "ls -l certificates/"]

# Private and public mapping
EXPOSE 40075/tcp

VOLUME /opentera

# env with a default value
ENV OPENTERA_CONFIG_PATH /opentera/teraserver/python/config/TeraServerConfig.ini
ENV VIDEODISPATCH_CONFIG_PATH /opentera/teraserver/python/services/VideoDispatch/VideoDispatchService.ini

# Run the required services and python script
CMD ls -l && ./start_docker.sh



