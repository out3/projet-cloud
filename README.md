# projet-cloud

## Architecture du docker-compose
- Docker-compose.yml
    - DockerFile
        - Image Ubuntu
        - Cmds >
            - Installation AWS CLI (Bash)
            - Scripts :
                - Déploiement infrastructure AWS (AWS CLI) -> 1 Master / X Slave
                - Installation Kubernetes (Bash) -> 1 Master AWS / X Slave AWS
                - Installation kube-opex-analytics (Bash) -> Sur Master Kubenetes
                - Installation Helm -> Sur Master Kubernetes
                - Déploiement application (Bash helm) -> Sur Master Kubenetes
                    - Application = Hadoop Spark

## notes
*   un pod = une application
*   le master et slave ne fonctionne jamais sur la même machine
*   le master est notre interface pour intéragir avec les slaves. Les requêtes sont envoyé au master donc on ne discute jamais avec les slaves
*   plusieurs VM = plusieurs EC2
*   Déploiement infrastructure AWS + récupération des VMs
*   spark = un pod kubernetes (on le déploie sur kubernetes)
    *   master kubernetes déploie des containers (workernodes)
    *   on indique commbien de workers il nous faut et il fait la gestion et allocation 
        *   ex : si on dit 6. Il va créer 6 worker et les partager entre les X slaves kubernetes
        *   si on a 2 slaves : il va déployer peut-être 3 workers dans chaque slave

## Liens
- https://spark.apache.org/docs/latest/running-on-kubernetes.html
- https://github.com/rchakode/kube-opex-analytics
- https://aws.amazon.com/fr/cli/


## Session du 02/12/2022
Objectif 1 : partir de rien pour créer infra Kubernetes
- Etape 1 : Création du Dockerfile qui déploie la VM principale avec Ubuntu : Jade et Alexandre
- Etape 2 : Ecrit le script qui créer les VMs sur AWS avec fichier conf : Philippe et Juliana 
- Etape 3 : Installer Kubernetes + Kubernetes analytics : à voir avancement


### Etape 1
<img width="712" alt="Capture d’écran 2022-12-12 à 14 35 04" src="https://user-images.githubusercontent.com/57618356/207058158-65810eea-e0b5-4eac-a7f0-a9b01e0c6dc0.png">
<img width="876" alt="Capture d’écran 2022-12-12 à 14 55 58" src="https://user-images.githubusercontent.com/57618356/207063273-c8f1f53c-809b-4bd8-8859-36088e6fa3ff.png">

