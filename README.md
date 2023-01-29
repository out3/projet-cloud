# Projet Cloud

## Introduction
Ce projet à pour contexte les cours d'Infrastructure Cloud et Infrastructure Big Data, de 3ème année SN à l'ENSEEIHT :
- [Sujet](docs/Sujet_2022.pdf)
- [Rapport de projet](docs/Rapport_2022.pdf)
- [Notes de réunions](docs/README.md)

## Prérequis
- Installer [Docker](https://docs.docker.com/engine/installation/)
- Installer [Docker Compose](https://docs.docker.com/compose/installation/)

## Configuration
1. Renommez le fichier `.env.template` en `.env`.
2. Remplissez les variables d'environnements dans le fichier `.env`. A savoir :
    - Les identifiants AWS$
    - Le nombre d'instances EC2 à créé

## Démarrage
Pour démarrer l'application, exécutez la commande suivante :

```
docker-compose up
```
