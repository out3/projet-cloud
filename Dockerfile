# DOCKER HNUB
FROM docker.io/library/ubuntu:latest

# Mise en place du dossier de travail
RUN mkdir /projet-cloud
WORKDIR /projet-cloud
VOLUME ["/projet-cloud"]

# Installation de python3 et des paquets requis
COPY requirements.txt /projet-cloud
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

