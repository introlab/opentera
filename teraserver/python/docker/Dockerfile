# Image: introlab3it/openteraserver

FROM ubuntu:18.04

# Install build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	postgresql redis-server build-essential cmake python3.6 git \
        python3-pip sudo vim libprotobuf-dev cmake

# Clone repository
# ARG CACHE_DATE=2019-04-25
RUN git clone -b dev https://github.com/introlab/opentera.git

# Install python packages
RUN pip3 install protobuf

#Create db and user
RUN service postgresql start &&\
	sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'test';"&&\
	sudo -u postgres psql -c "create database test" &&\
	sudo -u postgres psql -c "create user TeraAgent with encrypted password 'tera';"&&\
	sudo -u postgres psql -c "grant all privileges on database test to TeraAgent;"&&\
	sudo -u postgres psql -c "ALTER USER TeraAgent WITH PASSWORD 'tera';"&&\
	sudo -u postgres psql -c "\l"


WORKDIR /opentera/teraserver

# Everything is automated with cmake
RUN cmake
RUN make docker-all


# WORKDIR /opentera/teraserver/python
# Generate translations
# RUN pybabel extract -F babel.cfg -o translations.pot .
# RUN pybabel update -i translations.pot -d translations
# RUN pybabel compile -d translations

# Private and public mapping
EXPOSE 4040:4040

# Run the required services and python script
CMD ls -l && ./start.sh



