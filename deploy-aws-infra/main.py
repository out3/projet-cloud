import os, json
from utils.AWSSession import AWSSession, ClientError

_UBUNTU_AMI_ID = "ami-03b755af568109dc3"
_INSTANCE_TYPE = "t2.micro"

def main(session):
    try:
        # Création d'un VPC Réservé
        vpc = session.create_vpc("ProjetCloud-VPC", "192.168.0.0/24")
        vpc_id = vpc.id
        
        # Création d'une passerelle Internet
        internet_gateway = session.create_internet_gateway("ProjetCloud-InternetGateway")
        internet_gateway_id = internet_gateway.id
        session.attach_internet_gateway_to_vpc(internet_gateway, vpc)
        
        # Création d'un sous réseau lié au VPC
        subnet = session.create_subnet("ProjetCloud-Subnet", "192.168.0.0/24", vpc_id)
        subnet_id = subnet.id
        
        # On renomme la table de routage lié au VPC et on créée une route par défaut vers la passerelle
        session.setup_route_table_from_vpc("ProjetCloud-RoutingTable", vpc_id, internet_gateway_id)        
        
        # Création security group (fw)
        security_group = session.create_security_group(
            "ProjetCloud-SecurityGroup",
            "Security Group utilise pour le projet Infra",
            vpc_id
        )
        security_group_id = security_group.id
        
        # Création/Importation paire de clé
        key_pair_name = "ProjetCloud-KeyPair"
        key_pair = session.create_key_pair(key_pair_name)
        with open(f"./{key_pair_name}.pem", "w") as file:
            file.write(key_pair.key_material)
        os.chmod(f"{key_pair_name}.pem", 0o600)
        
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
        instances = []
        for i in ec2_instances:
            instances.append({
                "InstanceId": i.id,
                "InstanceIp": session.get_ec2_instance_public_ip(i.id)
            })
        
        data = {
            "VpcId" : vpc_id,
            "InternetGatewayId": internet_gateway_id,
            "SubnetId": subnet_id,
            "SecurityGroupId": security_group_id,
            "KeyPairPath": f"{os.getcwd()}/{key_pair_name}.pem",
            "Instances": instances
        }
        
    except ClientError as err:
        print(f"ClientError :\t{err}")
    except Exception as err:
        print(f"Exception :\t{err}")
    else:
        return data

def save_data_to_file(data):
    with open(f"inventory.json", "w") as file:
        json.dump(data, file)

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
    aws_data = main(session)
    save_data_to_file(aws_data)
