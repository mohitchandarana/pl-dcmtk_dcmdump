# Docker file for dcmtk_dcmdump ChRIS plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-dcmtk_dcmdump .
#
# In the case of a proxy (located at 192.168.13.14:3128), do:
#
#    docker build --build-arg http_proxy=http://192.168.13.14:3128 --build-arg UID=$UID -t local/pl-dcmtk_dcmdump .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pl-dcmtk_dcmdump
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-dcmtk_dcmdump
#

FROM fnndsc/python:3.8.5-ubuntu20.04
LABEL maintainer="Mohit <chandarana.m@northeastern.edu>"

RUN apt-get update && apt-get install -y dcmtk

WORKDIR /usr/local/src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["dcmtk_dcmdump", "--help"]
