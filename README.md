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
