import os
from utils.functions import *

_UBUNTU_AMI_ID = "ami-03b755af568109dc3"
_INSTANCE_TYPE = "t2.micro"

def main(session):
    try:
        # Création d'un VPC Réservé
        # vpc = session.create_vpc("ProjetCloud-VPC", "192.168.0.0/24")
        # vpc_id = vpc.id
        vpc_id = "vpc-0f6f8e31db4c99cd0"
        
        # Création d'un sous réseau lié au VPC
        # subnet = session.create_subnet("ProjetCloud-Subnet", "192.168.0.0/24", vpc_id)
        # subnet_id = subnet.id
        subnet_id = "subnet-0cf80af6fe82c24ec"
        
        
        # Création security group (fw)
        # security_group = session.create_security_group(
        #     "ProjetCloud-SecurityGroup",
        #     "Security Group utilise pour le projet Infra",
        #     vpc_id
        # )
        # security_group_id = security_group.id
        security_group_id = "sg-05e267f6b44a35f7e"
        
        # Création/Importation paire de clé
        # key_pair = session.create_key_pair("ProjetCloud-KeyPair")
        # key_pair_name = key_pair.name
        key_pair_name = "ProjetCloud-KeyPair"
        
        # Création VM EC2
        ec2_instances = session.create_ec2_instances(
            nb_instance = 2,
            name = "ProjetCloud-InstanceEC2",
            image_id = _UBUNTU_AMI_ID,
            instance_type =_INSTANCE_TYPE,
            security_group_id = security_group_id,
            subnet_id = subnet_id,
            key_pair_name = key_pair_name
        )
        ec2_instances_id = list(map(lambda x: x.id, ec2_instances))
        ec2_instances_ip = list(map(session.get_ec2_instance_public_ip, ec2_instances_id))
        
        
    except ClientError as err:
        print(err)

if __name__ == '__main__':
    # Setup env variables
    if not os.environ['AWS_ACCESS_KEY_ID']:
        print("AWS_ACCESS_KEY_ID undefined")
        exit()
    if not os.environ['AWS_SECRET_ACCESS_KEY']:
        print("AWS_SECRET_ACCESS_KEY undefined")
        exit()
    
    # Création session AWS
    session = AWSSession(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])
    # Appel de main
    main(session)