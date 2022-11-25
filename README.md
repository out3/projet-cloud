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
