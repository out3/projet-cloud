import argparse
import json
import os
import time

import paramiko
from termcolor import colored

def install_kubernetes(ip, port, user, ssh_key, verbose=False):
    # Banner
    print("###################################################")
    print(f"### {ip} : Kubernetes installation \t###")
    print("###################################################")

    # Connect to instance
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    # Install Docker
    cmd = "sudo swapoff -a"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            print("Error : ", cmd, exit_status)

    cmd = "wget -qO- https://get.docker.com/ | sh"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Install Kubernetes
    cmd = "sudo modprobe br_netfilter"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")
    
    cmd = """
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1 
EOF"""
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo sysctl --system"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = """
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF"""
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo apt-get update && sudo apt-get install -y kubelet kubeadm kubectl"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo sed -i 's|Environment=\"KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml\"|Environment=\"KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml --cgroup-driver=cgroupfs\"|' /etc/systemd/system/kubelet.service.d/10-kubeadm.conf"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo systemctl daemon-reload"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo rm /etc/containerd/config.toml && sudo systemctl restart containerd"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Close connection
    client.close()

def setup_master(ip, port, user, ssh_key, verbose=False):
    # Banner
    print("###########################################")
    print(f"### {ip} : Setup Master \t###")
    print("###########################################")

    # Connect to instance
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    # Configuration Kubernetes Master
    cmd = "sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=all --v=5"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "sudo kubeadm token create --print-join-command"
    output = client.exec_command(cmd)
    join_command = output[1].readline()

    cmd = "sudo mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Installation Helm
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
    
    # Close connection
    client.close()

    # Return Kubernetes Join Command
    return {
        "join_command": join_command.strip()
    }


def setup_worker(ip, port, user, ssh_key, master_join_command, verbose=False):
    # Banner
    print("###########################################")
    print(f"### {ip} : Setup workers \t###")
    print("###########################################")

    # Connect to instance
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    cmd = "sudo " + master_join_command + " --ignore-preflight-errors=all --v=5"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Close connection
    client.close()

def get_nodes(ip, port, user, ssh_key):
    # Banner
    print("###################################")
    print(f"### {ip} : Get nodes \t###")
    print("###################################")
    
    # Connect to instance
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    cmd = "kubectl get nodes && kubectl get pods --all-namespaces"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Close connection
    client.close()


def install_kube_opex(ip, port, user, ssh_key):
    # Banner
    print("#############################################")
    print(f"### {ip} : Install kube-opex-analytics \t###")
    print("#############################################")

    
    # Connect to instance
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, key_filename=ssh_key)

    cmd = "git clone https://github.com/rchakode/kube-opex-analytics.git"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")


    cmd = "kubectl create namespace kube-opex-analytics"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    cmd = "cd kube-opex-analytics && helm upgrade -n kube-opex-analytics --install kube-opex-analytics manifests/helm/"
    output = client.exec_command(cmd)
    if verbose:
        print_std(cmd, output, verbose)
    else:
        exit_status = output[1].channel.recv_exit_status()
        if exit_status == 0:
            print(cmd)
        else:
            raise Exception(f"[{exit_status}] Error : {cmd}")

    # Close connection
    client.close()

def print_std(command, output, verbose):
    stdin, stdout, stderr = output
    stdout = stdout.readlines()
    stderr = stderr.readlines()

    print(command)
    [print(colored(i, 'green')) for i in stdout]
    print()
    
    if verbose >= 2:
        [print(colored(i, 'red')) for i in stderr]
        print()


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
        # Install kubernetes
        install_kubernetes(_MASTER_IP, _PORT, _USER, _SSH_KEY, verbose)
        for ip in _WORKERS_IP:
            install_kubernetes(ip, _PORT, _USER, _SSH_KEY, verbose)

        # Setup master
        master = setup_master(_MASTER_IP, _PORT, _USER, _SSH_KEY, verbose)

        # Setup workers
        for ip in _WORKERS_IP:
            setup_worker(ip, _PORT, _USER, _SSH_KEY, master["join_command"], verbose)

        # Get nodes
        print("Waiting 30 secondes... (to be sure that all nodes are ready)")
        time.sleep(30)
        get_nodes(_MASTER_IP, _PORT, _USER, _SSH_KEY)

        # Install Kube-Opex
        # install_kube_opex(_MASTER_IP, _PORT, _USER, _SSH_KEY)
        # get_nodes(_MASTER_IP, _PORT, _USER, _SSH_KEY)
    except Exception as e:
        print(e)
