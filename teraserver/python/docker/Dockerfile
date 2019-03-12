# Image: introlab3it/openteraserver

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake python3.6 git \
	python3-pip

# Clone repository
RUN git clone -b dev https://github.com/introlab/opentera.git

# Install python packages
RUN pip3 install twisted \
    autobahn \
    sqlalchemy \
    psycopg2-binary \
    python-oauth2 \
    protobuf \
    flask \
    flask-sqlalchemy \
    flask-oauthlib \
    flask-login \
    flask-httpauth \
    flask-socketio \
    flask-session \
    redis \
    txredisapi \
    eventlet \
    gevent \
    gevent-websocket \
    passlib \
    bcrypt \
    wtforms \
    PyInstaller \
    pyopenssl \
    service_identity

WORKDIR /root



