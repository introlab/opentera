FROM ubuntu:22.04

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
RUN curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
RUN bash ~/nodesource_setup.sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs


# Add directory from host
ADD ../../../../teraserver ./teraserver


# Build environment
WORKDIR ./teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make python-all"]

ENV PYTHON3_EXEC ./teraserver/python/env/python-3.10/bin/python3



# RUN SERVER
WORKDIR ./teraserver/python
CMD ["python", "TeraServer.py"]

