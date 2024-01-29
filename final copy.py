import paramiko
import time
import re
from ipaddress import ip_network, ip_address
from netmiko import ConnectHandler

user = 'kbsl'
password = 'kbsl@123'
ip = '192.168.10.1'

#SSH to core switch
def ssh_to_core(ip, user, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print('Connecting to ', ip )
        ssh_client.connect(hostname=ip, username=user, password=password)

        shell = ssh_client.invoke_shell()
        shell.send('show arp\n') 

        time.sleep(1)

        output = shell.recv(65535).decode("utf-8")  # Receive output

        with open('arp_table.txt', 'w') as file:
            file.write(output)  # Write output to a file

        print("ARP table saved to arp_table.txt")
        return output

    except paramiko.AuthenticationException:
        print(f"Authentication failed for {ip}.")
    except paramiko.SSHException as e:
        print(f"SSH connection to {ip} failed: {e}")
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")
    finally:
        # Close the SSH connection
        print("Closing connection.. ")
        ssh_client.close()


def print_ip():
    # Read the contents of the file
    with open('arp_table.txt', 'r') as file:
        arp_table = file.read()

    # Use regular expressions to find IP addresses
    ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', arp_table)

    if not ip_addresses:
        print("No IP addresses found in ARP table!")
        return
    else:
        # Print the extracted IP addresses
        print("Ip address..\n")
        for ip in ip_addresses:
            print(ip)

        return ip_addresses


def filter_management_ips(ip_addresses, management_subnet):
        
        # Convert management subnet to network object
        management_network = ip_network(management_subnet, strict=False)
     
        # Filter IP addresses belonging to the management subnet
        management_ips = [ip for ip in ip_addresses if ip_address(ip) in management_network]
     
        return management_ips

def save_ips_to_file(ips, filename):
    with open(filename, 'w') as file:
        for ip in ips:
            file.write(ip + '\n')

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

        print("SSH config of all switches are done")

    except Exception as e:
        print("Failed to connect:", str(e))

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

    
def exe_commands_to_hosts2(user, password, management_ips, commands):
    for ip in management_ips:
        try:
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
                # print(f"Output for command '{command}':")
                # print(output.decode())  # Decode the bytes to string for readability
                time.sleep(1)
            print("Done " + ip)
            ssh_client.close()

        except Exception as e:
            print(f"Failed to connect to {ip}: {str(e)}")
            continue  # Move to the next IP even if there's an exception

    print("Done")


def config_ssh2(ips):
    for ip in ips:
        try:
            device = {
                'device_type': 'cisco_ios_telnet',
                'ip': ip,
                'username': 'test',
                'password': 'Kbsl@123',
                'port': 23
            }
            net_connect = ConnectHandler(**device)
            print("Connected to ", ip)

            output = net_connect.send_config_set(['crypto key generate rsa general-keys modulus 1024', '\n', '\n', 'ip ssh version 2'])
            print(output)

            net_connect.disconnect()
            print("Disconnected from ", ip)

        except Exception as e:
            print(f"Failed to connect to {ip}: {str(e)}")
            continue  # Move to the next IP even if there's an exception


def main():

    # Input the Cisco switch details
    switch_ip = input("Enter the Cisco switch IP address: ")
    username = 'kbsl'
    password = 'kbsl@123'

    # SSH and get ARP table
    ssh_to_core(switch_ip,username,password)

    # Get Ip 
    ip_addresses = print_ip()

    # Input the management subnet
    management_subnet = input("Enter the management subnet (e.g., 192.168.20.0/24): ")

    management_ips = filter_management_ips(ip_addresses,management_subnet)

    if not management_ips:
        print("No management IP found!")
        return
    
    save_ips_to_file(management_ips, 'management_ips.txt')
    print("\nManagement IPs saved in management_ips.txt:")
    for ip in management_ips:
        print(ip)
        
    config_ssh2(management_ips) 

    commands_to_execute = [
    'enable',
    'cisco',
    'configure terminal',
    'int loop 10',
    'exit',
    'vlan 20',
    'name FINANCE',
    'exit',
    'end',
    'copy running-config startup-config',
    '\n',
    'reload',
    '\n'] 
    
    user1 = 'test'
    password1 = 'Kbsl@123'

    exe_commands_to_hosts2(user1, password1, management_ips,commands_to_execute)
    

if __name__ == "__main__":
    main()