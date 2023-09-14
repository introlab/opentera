FROM python:3.11.5-bullseye

# Install requirements (not changing often)
ADD ./teraserver/python/env/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Add directory from host
ADD ./teraserver ./teraserver

# Generate certificates
WORKDIR /teraserver/python
RUN python ./CreateCertificates.py

# Will keep the container running.
CMD ["/bin/sh", "-c", "trap exit 1 INT; while true; do sleep 1; done"]
