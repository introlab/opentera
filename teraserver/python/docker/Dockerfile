# Image: introlab3it/openteraserver

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake python3.6 git

RUN git clone -b dev https://github.com/introlab/opentera.git


WORKDIR /root



