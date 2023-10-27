FROM python:3.11.5-bullseye

# Change default shell to bash
SHELL ["/bin/bash", "-c"]

# Install build dependencies
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
	build-essential cmake git sudo vim libprotobuf-dev protobuf-compiler locales wget curl python3 

# Install openssh-server
# RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y openssh-server

# Set system locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Create dev user with no password
#RUN ["/bin/bash", "-c", "useradd -m -s /bin/bash dev"]
#RUN ["/bin/bash", "-c", "echo 'dev:dev' | chpasswd"]
#RUN ["/bin/bash", "-c", "echo 'dev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"]
#RUN ["/bin/bash", "-c", "passwd -d dev"]

# Enable open-ssh server
#RUN ["/bin/bash", "-c", "mkdir /var/run/sshd"]
#RUN ["/bin/bash", "-c", "echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config"]
#RUN ["/bin/bash", "-c", "echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config"]
#RUN ["/bin/bash", "-c", "echo 'PermitEmptyPasswords yes' >> /etc/ssh/sshd_config"]
#RUN ["/bin/bash", "-c", "echo 'PermitUserEnvironment yes' >> /etc/ssh/sshd_config"]
#RUN ["/bin/bash", "-c", "echo 'X11Forwarding yes' >> /etc/ssh/sshd_config"]

WORKDIR /

# Add requirements (will be cached and build faster, path relative to context)
ADD ./teraserver/python/env/requirements.txt /requirements.txt
RUN ["/bin/bash", "-c", "python3 -m pip install -r /requirements.txt"]

# Install latest npm / nodejs
RUN curl -sL https://deb.nodesource.com/setup_18.x -o /nodesource_setup.sh
RUN bash /nodesource_setup.sh
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y nodejs

# Add directory from host (path relative to context)
ADD ./teraserver /teraserver

# Remove local environment that was copied in the ADD command if it exists
RUN if [ -d "/teraserver/python/env/python-3.11" ]; then rm -rf /teraserver/python/env/python-3.11; fi

# Cleanup directory of cmake cache (we possibly are using it outside of docker)
RUN if [ -f "/teraserver/CMakeCache.txt" ]; then rm -f /teraserver/CMakeCache.txt; fi

# Install node-js signaling server
WORKDIR /teraserver/easyrtc
RUN ["/bin/bash", "-c", "npm install"]

# Build environment
WORKDIR /teraserver
RUN ["/bin/bash", "-c", "cmake ."]
RUN ["/bin/bash", "-c", "make docker-python-all"]

# Set Python path
ENV PYTHONPATH /teraserver/python

# RUN SERVER
WORKDIR /teraserver/python

# RUN SSH SERVER AND TERA SERVER
CMD ["/bin/bash", "-c", "python3 -m debugpy --listen 0.0.0.0:5678 TeraServer.py"]
