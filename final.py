import paramiko
import time
import re
from ipaddress import ip_network, ip_address
from netmiko import ConnectHandler

user = 'kbsl'
password = 'kbsl@123'
ip = '192.168.10.1'

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
        print("Done "+ip)
        ssh_client.close()

    print("Done")
    
def config_ssh(ips):
    try:
        for ip in ips:

            device = {'device_type': 'cisco_ios_telnet','ip': ip,'username': 'test','password': 'Kbsl@123','port': 23}
            net_connect = ConnectHandler(**device)
            print("Connected to the ", ip)

            # Send commands or interact with the switch
            output = net_connect.send_config_set(['crypto key generate rsa general-keys modulus 1024', '\n', '\n', 'ip ssh version 2'])
            print(output)
            # Disconnect from the device
            net_connect.disconnect()
            print("Disconnected from ",ip)

    except Exception as e:
        print("Failed to connect:", str(e))


commands_to_execute = [
    'enable',
    'cisco',
    'configure terminal',
    'int loop 10',
    'end'
]



management_ips = exe_ssh1(ip,user,password)
config_ssh(management_ips)

exe_commnds_to_hosts(user,password,management_ips,commands_to_execute)