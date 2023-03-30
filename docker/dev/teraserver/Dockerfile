FROM ubuntu:22.04

# Change default shell to bash
SHELL ["/bin/bash", "-c"]

# Install build dependencies
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
	build-essential cmake git sudo vim libprotobuf-dev protobuf-compiler locales wget curl openssh-server

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Create dev user with no password
RUN ["/bin/bash", "-c", "useradd -m -s /bin/bash dev"]
RUN ["/bin/bash", "-c", "echo 'dev:dev' | chpasswd"]
RUN ["/bin/bash", "-c", "echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"]

# Enable open-ssh server
RUN ["/bin/bash", "-c", "mkdir /var/run/sshd"]
RUN ["/bin/bash", "-c", "echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config"]
RUN ["/bin/bash", "-c", "echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config"]
RUN ["/bin/bash", "-c", "echo 'PermitEmptyPasswords yes' >> /etc/ssh/sshd_config"]
RUN ["/bin/bash", "-c", "echo 'PermitUserEnvironment yes' >> /etc/ssh/sshd_config"]
RUN ["/bin/bash", "-c", "echo 'X11Forwarding yes' >> /etc/ssh/sshd_config"]


# Install miniconda
WORKDIR /root
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3


# Install latest npm / nodejs
RUN curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
RUN bash ~/nodesource_setup.sh
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# Add directory from host
ADD ../../../../teraserver /root/teraserver

# Remove local environment that was copied in the ADD command if it exists
RUN if [ -d "/root/teraserver/python/env/python-3.10" ]; then rm -rf /root/teraserver/python/env/python-3.10; fi

# Install node-js signaling server
WORKDIR /root/teraserver/easyrtc
RUN ["/bin/bash", "-c", "npm install"]

# Build environment
WORKDIR /root/teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make python-env"]

ENV PYTHON3_EXEC /root/teraserver/python/env/python-3.10/bin/python3

# Set Python path
ENV PYTHONPATH /root/teraserver/python

# RUN SERVER
WORKDIR /root/teraserver/python

# RUN SSH SERVER AND TERA SERVER
CMD ["/bin/bash", "-c", "/usr/sbin/sshd -D; $PYTHON3_EXEC TeraServer.py"]


