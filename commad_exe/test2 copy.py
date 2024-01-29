import paramiko
import time
import re
from ipaddress import ip_network, ip_address

user = 'kbsl'
password = 'kbsl@123'
ip = '192.168.10.1'

def exe_ssh(ip, user, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to.. ', ip )
    ssh_client.connect(hostname=ip, username=user, password=password)

    shell = ssh_client.invoke_shell()
    shell.send('show run')
    print("Closing connection.. ")
    ssh_client.close()

#SSH to core switch
def exe_ssh1(ip, user, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to.. ', ip )
    ssh_client.connect(hostname=ip, username=user, password=password)

    shell = ssh_client.invoke_shell()
    shell.send('show arp\n')  # Use 'show arp' instead of 'show run'

    time.sleep(2)  # Adjust sleep time if needed for the command to execute

    output = shell.recv(65535).decode("utf-8")  # Receive output

    with open('arp_table.txt', 'w') as file:
        file.write(output)  # Write output to a file

    print("ARP table saved to arp_table.txt")
    print("Closing connection.. ")
    ssh_client.close()
    
    management_ips = print_ip()
    return management_ips

def print_ip():
    # Read the contents of the file
    with open('arp_table.txt', 'r') as file:
        arp_table = file.read()

    # Use regular expressions to find IP addresses
    ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', arp_table)

    # Print the extracted IP addresses
    print("Ip address..")
    for ip in ip_addresses:
        print(ip)

    management_subnet = input("Enter management subnet:")

    management_ips = filter_management_ips_from_file('arp_table.txt',management_subnet)
    return management_ips

def filter_management_ips_from_file(file_path, management_subnet):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        arp_table = file.read()

    # Use regular expressions to find IP addresses
    ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', arp_table)

    def filter_management_ips(ip_addresses, management_subnet):
        # Convert management subnet to network object
        management_network = ip_network(management_subnet, strict=False)
     
        # Filter IP addresses belonging to the management subnet
        management_ips = [ip for ip in ip_addresses if ip_address(ip) in management_network]
     
        return management_ips

    # Filter IP addresses within the management subnet
    management_ips = filter_management_ips(ip_addresses, management_subnet)
    print("Mngt Ip address..")
    for ip in management_ips:
        print(ip)

    return management_ips

def exe_commnds_to_hosts_save_arp(user, password, management_ips):
    for ip in management_ips:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print('Connecting to.. ', ip)
        ssh_client.connect(hostname=ip, username=user, password=password)

        shell = ssh_client.invoke_shell()
        shell.send('show arp\n')
        time.sleep(2)

        output = shell.recv(65535).decode("utf-8")

        # Save ARP table with IP address in the file name
        file_name = f"{ip}_arp_table.txt"
        with open(file_name, 'w') as file:
            file.write(output)

        print(f"ARP table saved to {file_name}")
        print("Closing connection.. ")
        ssh_client.close()
        
def exe_commnds_to_hosts(user, password, management_ips,commands):
    for ip in management_ips:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print('Connecting to.. ', ip)
        ssh_client.connect(hostname=ip, username=user, password=password)

        shell = ssh_client.invoke_shell()

        for command in commands:
            shell.send(command + '\n')
            while not shell.recv_ready():
                pass
            output = shell.recv(65535).decode("utf-8")
            #print(f"Output for command '{command}':")
            #print(output.decode())  # Decode the bytes to string for readability
            time.sleep(1)
        print(ip+"- Done")
        ssh_client.close()

    print("Done")
    
commands_to_execute = [
    'enable',
    'cisco',
    'configure terminal',
    'int loop 10',
    'end'
]


management_ips = exe_ssh1(ip,user,password)
exe_commnds_to_hosts(user,password,management_ips,commands_to_execute)