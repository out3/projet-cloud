import boto3
from botocore.exceptions import ClientError

class AWSSession:
    """
    Classe fournissant une série de fonctions simplifiées
    afin de gérer l'environnement AWS
    """
    def __init__(self, aws_acces_key_id : str, aws_secret_access_key : str) -> None:
        """
        Initialisation de la session AWS à partir des identifiants
        récupérés sur le compte personnel

        Args:
            aws_acces_key_id (str)
            aws_secret_access_key (str)
        """
        self.session = boto3.session.Session(
            aws_access_key_id = aws_acces_key_id,
            aws_secret_access_key = aws_secret_access_key,
            region_name = "eu-west-3"
        )
        
    ###
    # KEY PAIR
    ###
    def create_key_pair(self, name: str) -> dict:
        """
        Création d'un nune nouvelle paire de clé

        Args:
            name (str): Nom de la paire de clé

        Returns:
            dict: ec2.KeyPair
        """
        client = self.session.resource('ec2')
        try:
            new_key_pair = client.create_key_pair(
                KeyName = name,
                KeyType = "rsa",
                KeyFormat = "pem"
            )
        except ClientError:
            raise
        else:
            return new_key_pair
        
    ###
    # VPC
    ###
    def create_vpc(self, name: str, cidr: str) -> dict:
        """
        Création d'un nouveau VPC

        Args:
            name (str): Nom du VPC
            cidr (str): CIDR du VPC sous le format X.X.X.X/XX

        Returns:
            dict: ec2.Vpc
        """
        client = self.session.resource('ec2')
        try:
            new_vpc = client.create_vpc(
                CidrBlock = cidr,
                TagSpecifications = [
                    {
                        "ResourceType": "vpc",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": name
                            }
                        ]
                    }
                ]
            )
        except ClientError:
            raise
        else:
            return new_vpc
    
    ###
    # SUBNET
    ###
    def create_subnet(self, name: str, cidr:str, vpc_id: str) -> dict:
        """
        Création d'un nouveau sous-réseau

        Args:
            name (str): Nom du sous-réseau
            cidr (str): CIDR du sous-réseau sous le format X.X.X.X/XX
            vpc_id (str): ID du VPC auquel lié le nouveau sous-réseau

        Returns:
            dict: ec2.Subnet
        """
        client = self.session.resource('ec2')
        try:
            new_subnet = client.create_subnet(
                CidrBlock = cidr,
                VpcId = vpc_id,
                TagSpecifications = [
                    {
                        "ResourceType": "subnet",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": name
                            }
                        ]
                    }
                ]
            )
        except ClientError:
            raise
        else:
            return new_subnet
    
    
    ###
    # Security Group
    ###
    def create_security_group(self, name: str, description: str, vpc_id:str) -> dict:
        """
        Créé un nouveau groupe de sécurité et ouvre tous les flux entrants

        Args:
            name (str): Nom du groupe de sécurité
            description (str): Description du groupe de sécurité
            vpc_id (str): ID du VPC lié au groupe de sécurité

        Returns:
            dict: ec2.securityGroup
        """
        client = self.session.resource('ec2')
        try:
            # Création du Security Group
            new_security_group = client.create_security_group(
                GroupName = name,
                Description = description,
                VpcId = vpc_id
            )
            security_group_id = new_security_group.id
            
            # # Mise à jour des règles de sécurités => Ouverture totale
            flow_ingress = new_security_group.authorize_ingress(
                GroupId = security_group_id,
                IpPermissions = [
                    {
                        'IpProtocol': '-1',
                        'FromPort': 0,
                        'ToPort': 65535,
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': '[Temporaire] Ouverture de tous les flux pour faciliter le projet'
                            }
                        ]
                    }
                ]
            )           
        except ClientError:
            raise
        else:
            return new_security_group
    
    ###
    # EC2 Instances
    ###
    def create_ec2_instances(self,
        nb_instance: int,
        name: str,
        image_id: str,
        instance_type: str,
        security_group_id: str,
        subnet_id: str,
        key_pair_name: str
    ) -> dict:
        """
        Créé de nouvelles instances EC2

        Args:
            nb_instance (int): Nomdre d'instance EC2 à créer
            name (str): Nom de l'instance EC2
            image_id (str): ID de l'image sur laquelle se base les nouvelles instances
            instance_type (str): Type de l'instance
            security_group_id (str): ID du groupe de sécurité
            subnet_id (str): ID du sous-réseau
            key_pair_name (str): Nom de la paire de clé RSA

        Returns:
            dict: ec2.Instance
        """
        client = self.session.resource('ec2')
        try: 
            new_ec2_instances = client.create_instances(
                
                ImageId = image_id,
                MinCount = nb_instance,
                MaxCount = nb_instance,
                InstanceType = instance_type,
                # SecurityGroupIds = [security_group_id],
                # SubnetId = subnet_id,
                NetworkInterfaces=[{
                    "DeviceIndex": 0,
                    "Groups": [security_group_id],
                    "SubnetId": subnet_id,
                    "AssociatePublicIpAddress": True
                }],
                KeyName = key_pair_name,
                TagSpecifications = [
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": name
                            }
                        ]
                    }
                ]
            )
            for instance in new_ec2_instances:
                print(f"Instance {instance} en cours de création...")
            for instance in new_ec2_instances:
                instance.wait_until_exists()
                print(f"Instance {instance} créée.")
            for instance in new_ec2_instances:
                instance.wait_until_running()
                print(f"Instance {instance} fonctionnelle.")
        except ClientError:
            raise
        else:
            return new_ec2_instances
        
    def get_ec2_instance_public_ip(self, instance_id: str):
        client = self.session.client('ec2')
        try:
            ec2_instance = client.describe_instances(
                InstanceIds = [instance_id]
            )
            ec2_instance_ip = ec2_instance["Reservations"][0]["Instances"][0]["PublicDnsName"]            
        except ClientError:
            raise
        else:
            return ec2_instance_ip
