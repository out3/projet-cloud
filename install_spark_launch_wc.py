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
    cmd = """
    kubectl exec -ti --namespace default """ + _SPARK_CLUSTER_NAME +"-worker-0 -- " + """
    spark-submit --master spark://""" + _SPARK_CLUSTER_NAME + """-master-svc:7077  
    --class org.apache.spark.examples.SparkPi """ + _EXAMPLE_JAR + " 2"
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
    
    # Make sure WordCount application is not corrupt
    cmd =  "jar tf "+ "./projet-cloud/"+ _MYAPP
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
    cmd =  "kubectl cp ./projet-cloud/"+ _MYAPP +" default/"+ _SPARK_CLUSTER_NAME + "-worker-0:/opt/bitnami/spark/tmp/"
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
    cmd =  """
    cat <<EOF | tee impvc0.yaml
    kind: PersistentVolume
    apiVersion: v1
    metadata:
    name: impvc
    labels:
        name: impvc
    spec:
    capacity:
        storage: 2Gi
    storageClassName: standard
    accessModes:
        - ReadOnlyMany
    gcePersistentDisk:
        pdName: myvols
        fsType: ext4
        readOnly: true
    EOF

    kubectl apply -f impvc0.yaml -n default
    """
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
    cmd =  """
    cat <<EOF | tee impvc1.yaml
    kind: PersistentVolumeClaim
    apiVersion: v1
    metadata:
    name: impvc
    spec:
    storageClassName: standard
    accessModes:
        - ReadOnlyMany
    resources:
        requests:
        storage: 2Gi
    selector:
        matchLabels:
        name: impvc
    EOF 

    kubectl apply -f impvc1.yaml -n default
    """
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
    cmd =  """
    kubectl exec -ti --namespace default """ +_SPARK_CLUSTER_NAME+"""-worker-0 -- spark-submit \
    --master spark://spark://""" + _SPARK_CLUSTER_NAME + """-master-svc:7077 --class wc.WordCount  \
    --conf spark.eventLog.enabled=true \
    --conf spark.eventLog.dir=/opt/bitnami/spark/tmp \
    --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.impvc.options.claimName=impvc \
    --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.impvc.mount.path=/opt/bitnami/spark/tmp \
    --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.impvc.options.claimName=impvc \
    --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.impvc.mount.path=/opt/bitnami/spark/tmp \
    """ + "tmp/"+_MYAPP
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
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Copy and read result
    cmd =  """
    kubectl cp default/""" +_SPARK_CLUSTER_NAME + """-worker-0:/opt/bitnami/spark/tmp/result/part-0000 . ;
    tail -n 20 part-0000
    """
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    print("The end")