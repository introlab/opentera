# Image: introlab3it/openteraserver
# LABEL version="0.1"
# LABEL description="OpenTera Test Server from IntRoLab."

#FROM resin/armv7hf-debian-qemu
# FROM balenalib/rpi-raspbian
FROM balenalib/armv7hf-debian-python
RUN [ "cross-build-start" ]

# Install build dependencies
RUN apt-get update && apt-get upgrade && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	redis-server build-essential cmake git sudo vim libprotobuf-dev \
	cmake protobuf-compiler locales wget curl nginx

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Clone repository
ARG CACHE_DATE=2020-06-11
RUN git clone --recurse-submodules -b dev https://github.com/introlab/opentera.git


# Install miniconda
# WORKDIR /root
# RUN wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
# RUN bash ~/Miniconda3-latest-Linux-armv7l.sh -h
# RUN bash ~/Miniconda3-latest-Linux-armv7l.sh -f -b -p $HOME/miniconda3

# Install latest npm / nodejs
RUN wget -qO- https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# Install database
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql

#Create dbs and users
RUN service postgresql start &&\
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'test';"&&\
	sudo -u postgres psql -c "create database test" &&\
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"&&\
	sudo -u postgres psql -c "grant all privileges on database test to TeraAgent;"&&\
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"&&\
	sudo -u postgres psql -c "create database openteralogs" &&\
	sudo -u postgres psql -c "grant all privileges on database openteralogs to TeraAgent;"&&\
	sudo -u postgres psql -c "create database openterafiles" &&\
	sudo -u postgres psql -c "grant all privileges on database openterafiles to TeraAgent;"&&\
	sudo -u postgres psql -c "\l"

#VOLUME
RUN mkdir /config
VOLUME /config

# Install python
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-setuptools python3-dev libffi-dev libssl-dev libpq-dev

# Install python deps
WORKDIR /opentera/teraserver/python/env

RUN pip3 install wheel
RUN pip3 install -r requirements.txt

# Build environment
WORKDIR /opentera/teraserver
#RUN ["/bin/bash", "-c", "cmake ."]
RUN cmake .
#RUN ["/bin/bash", "-c", "make docker-all"]
RUN make docker-all

#ENV PYTHON3_EXEC /opentera/teraserver/python/env/python-3.6/bin/python3
ENV PYTHON3_EXEC /usr/bin/python3

# Install nodejs package
WORKDIR /opentera/teraserver/easyrtc
RUN npm install

# Final working directory
WORKDIR /opentera/teraserver/python

# Create certificates from new python env
# RUN ["/bin/bash", "-c", "$PYTHON3_EXEC ./CreateCertificates.py"]
RUN $PYTHON3_EXEC ./CreateCertificates.py
# RUN ["/bin/bash", "-c", "ls -l certificates/"]
RUN ls -l certificates/

# Private and public mapping
EXPOSE 40075/tcp

# env with a default value
ENV OPENTERA_CONFIG_PATH /opentera/teraserver/python/config/TeraServerConfig.ini
ENV VIDEODISPATCH_CONFIG_PATH /opentera/teraserver/python/services/VideoDispatch/VideoDispatchService.ini

# Create nginx logs directory
RUN mkdir -p config/logs

# Set Python path
ENV PYTHONPATH /opentera/teraserver/python

# Run the required services and python script
CMD nginx -c /opentera/teraserver/python/config/nginx.conf -p /opentera/teraserver/python/config/ && ./start_docker.sh

RUN [ "cross-build-end" ]



