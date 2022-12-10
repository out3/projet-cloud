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
    # KeyPair
    ###
    def create_key_pair(self, name: str) -> dict:
        """
        Création d'un nune nouvelle paire de clé

        Args:
            name (str): Nom de la paire de clé

        Returns:
            dict: ec2.KeyPair
        """
        resource = self.session.resource('ec2')
        try:
            new_key_pair = resource.create_key_pair(
                KeyName = name,
                KeyType = "rsa",
                KeyFormat = "pem"
            )
        except ClientError:
            raise
        else:
            return new_key_pair
        

    ###
    # Vpc
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
        resource = self.session.resource('ec2')
        client = self.session.client('ec2')
        try:
            # Création du VPC
            new_vpc = resource.create_vpc(
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
            new_vpc.wait_until_available()
            # Activation du DNS publique
            client.modify_vpc_attribute(
                VpcId = new_vpc.id,
                EnableDnsHostnames = {
                    "Value": True
                }
            )
        except ClientError:
            raise
        else:
            return new_vpc
    
    ###
    # InternetGateway
    ###
    def create_internet_gateway(self, name: str) -> dict:
        resource = self.session.resource('ec2')
        try:
            # On créé la passerelle Internet
            new_internet_gateway = resource.create_internet_gateway(
                TagSpecifications = [
                    {
                        "ResourceType": "internet-gateway",
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
            return new_internet_gateway
    
    def attach_internet_gateway_to_vpc(self, internet_gateway: dict, vpc: dict):
        try:
            vpc.attach_internet_gateway(
                InternetGatewayId = internet_gateway.id
            )
        except ClientError:
            raise
        
    ###
    # Subnet
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
        resource = self.session.resource('ec2')
        client = self.session.client('ec2')
        try:
            new_subnet = resource.create_subnet(
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
            # On permet le sous-réseau d'attribuer des adresses IP publique aux nouvelles isntances
            client.modify_subnet_attribute(
                SubnetId = new_subnet.id,
                MapPublicIpOnLaunch = {
                    "Value": True
                }
            )
        except ClientError:
            raise
        else:
            return new_subnet
    
    ###
    # RouteTable
    ###
    def setup_route_table_from_vpc(self, name: str, vpc_id: str, internet_gateway_id: str):
        client = self.session.client('ec2')
        resource = self.session.resource('ec2')
        try:
            # On récupère l'id de la RouteTable
            new_route_table = client.describe_route_tables(
                Filters = [
                    {
                        "Name": "vpc-id",
                        "Values": [ vpc_id ] 
                    }
                ]
            )
            new_route_table_id = new_route_table["RouteTables"][0]["RouteTableId"]
            # On donne un nom à la RouteTable
            resource.RouteTable(new_route_table_id).create_tags(
                Tags = [
                    {
                        "Key": "Name",
                        "Value": name
                    }
                ]
            )
            # On créer une route statique par défaut vers la gateway
            client.create_route(
                DestinationCidrBlock = "0.0.0.0/0",
                GatewayId = internet_gateway_id,
                RouteTableId = new_route_table_id
            )
        except ClientError:
            raise    
    
    ###
    # SecurityGroup
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
        resource = self.session.resource('ec2')
        try:
            # Création du Security Group
            new_security_group = resource.create_security_group(
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
    # Instances
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
        resource = self.session.resource('ec2')
        try: 
            new_ec2_instances = resource.create_instances(
                
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
        
    def get_ec2_instance_public_ip(self, instance_id: str) -> str:
        """
        Récupère l'adresse IP publique d'une instance EC2

        Args:
            instance_id (str): Id de l'instance

        Returns:
            str: Adresse IP publique de l'instance
        """
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
