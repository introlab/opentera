FROM python:3.11-trixie

# Install requirements (not changing often)
ADD ./teraserver/python/env/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Add directory from host
ADD ./teraserver ./teraserver

WORKDIR /teraserver/python

# Generate certificates at startup into the certificates volume (only if they do not exist yet),
# then keep the container running.
CMD ["/bin/sh", "-c", "python ./CreateCertificates.py && trap exit 1 INT; while true; do sleep 1; done"]
