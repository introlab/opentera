FROM python:3.10-bullseye

# Add directory from host
ADD ../../../../teraserver ./teraserver
RUN ls -l ./teraserver
RUN pip install -r ./teraserver/python/env/requirements.txt
# Generate certificates
WORKDIR ./teraserver/python
RUN python ./CreateCertificates.py
# Will keep the container running.
CMD ["/bin/sh", "-c", "trap exit 1 INT; while true; do sleep 1; done"]