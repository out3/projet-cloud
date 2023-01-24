import argparse
import json
import os
import time
import re

import paramiko
from termcolor import colored

def install_spark(ip, port, user, ssh_key, verbose=False):
    #variables
    _SPARK_CLUSTER_NAME = "spark-cluster"
    _MYAPP = "wc.jar"
    _EXAMPLE_JAR = "examples/jars/spark-examples_2.12-3.3.1.jar"

    # Banner
    print("########################################################################")
    print(f"### {ip} : Helm Spark Bitnami installations + Wordcount launch \t###")
    print("########################################################################")

    # Connect to instance (master) using paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    # Install helm
    cmd = "curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")
    
    # Add binami spark chart
    cmd = "helm repo add bitnami https://charts.bitnami.com/bitnami"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Create a spark cluster using spark charts 
    cmd = "helm install "+ _SPARK_CLUSTER_NAME + " bitnami/spark"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")
    
    # Test example 
    cmd = "kubectl exec -ti --namespace default " + _SPARK_CLUSTER_NAME +"-worker-0 -- " + "spark-submit --master spark://" + _SPARK_CLUSTER_NAME + "-master-svc:7077  --class org.apache.spark.examples.SparkPi " + _EXAMPLE_JAR + " 2"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Download the WordCount application
    cmd =  "git clone https://github.com/out3/projet-cloud.git"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Install jdk
    cmd =  "apt-get -y install default-jdk"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Make sure WordCount application is not corrupt
    cmd =  "jar tf "+ "./projet-cloud/03-Spark/"+ _MYAPP
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")
    
    # Copy WordCount application into pod 
    cmd =  "kubectl cp ./projet-cloud/03-Spark/"+ _MYAPP +" default/"+ _SPARK_CLUSTER_NAME + "-worker-0:/opt/bitnami/spark/tmp/"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Create a pv
    cmd =  "kubectl apply -f ./projet-cloud/03-Spark/impvc0.yaml -n default"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    #Create a pvc
    cmd =  "kubectl apply -f ./projet-cloud/03-Spark/impvc1.yaml -n default"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    #verify bound status between the pv & pvc
    cmd =  " kubectl get pvc | grep 'impvc' | tr -cs '[:alnum:]' '\n' | grep 'Bound'"
    output = client.exec_command(cmd)
    if verbose:
        print(cmd)
        if re.search("Bound", output[1].read().decode()) != None:
            print("OK, pvc  bounded")
        else:
            print("\n Sorry, pvc or pv not bounded \n")
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    #Launch the WordCount application via spark-submit
    cmd =  "kubectl exec -ti --namespace default " +_SPARK_CLUSTER_NAME+"-worker-0 -- spark-submit --master spark://" + _SPARK_CLUSTER_NAME + "-master-svc:7077 --class wc.WordCount --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=/opt/bitnami/spark/tmp --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.impvc.options.claimName=impvc --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.impvc.mount.path=/opt/bitnami/spark/tmp --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.impvc.options.claimName=impvc --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.impvc.mount.path=/opt/bitnami/spark/tmp" + " tmp/"+_MYAPP + " /opt/bitnami/spark/NOTICE"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")
    
    # Find result in stored in pod
    cmd =  "kubectl exec -ti --namespace default " + _SPARK_CLUSTER_NAME + "-worker-0 -- ls -l /opt/bitnami/spark/tmp/result"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
            print(output[1].read().decode())
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Copy and read result
    cmd =  "kubectl exec -ti --namespace default " + _SPARK_CLUSTER_NAME + "-worker-0 -- cat /opt/bitnami/spark/tmp/result/part-00000"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
            print(output[1].read().decode())
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    print("The end")
    
if __name__ == '__main__':
    # Arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="count")
    verbose = parser.parse_args().verbose
    
    # Setup vars
    with open(f"{os.path.dirname(__file__)}/../01-deploy-aws-infra/inventory.json", 'r') as file:
        _DATA = json.load(file)
    _SSH_KEY = _DATA["KeyPairPath"]
    _PORT = 22
    _USER = "ubuntu"
    _MASTER_IP = _DATA["Instances"][0]["InstanceIp"]
    _WORKERS_IP = [i["InstanceIp"] for i in _DATA["Instances"][1:]]
    try:
        # Install spark & execute word count
        install_spark(_MASTER_IP, _PORT, _USER, _SSH_KEY, verbose)

    except Exception as e:
        print(e)
