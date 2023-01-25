# Initialisation
FROM ubuntu:22.04
RUN apt-get update
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install wget
# Installation de pip
RUN apt-get -y install python3-distutils
RUN wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
# Installation de botocore
RUN python3 /tmp/get-pip.py
RUN pip3 install botocore
# Installation de boto3
RUN apt-get install -y python3-boto3
# Installation de jmespath
RUN pip3 install jmespath
# Installation de python-dateutil
RUN pip3 install python-dateutil
# Installation de s3transfer
RUN apt-get install -y python3-s3transfer
# Installation du module six
RUN pip3 install six
# Installation de urllib3
RUN pip3 install urllib3
RUN pip3 install paramiko
RUN python3 -m pip install --upgrade termcolor
RUN apt install python3-dotenv

