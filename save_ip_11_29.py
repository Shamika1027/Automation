import paramiko
import time
import re
from ipaddress import ip_network, ip_address
from netmiko import ConnectHandler
import pandas as pd

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

        with open('arp_table1.txt', 'w') as file:
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


def print_ip_and_mac():
    # Read the contents of the file
    with open('arp_table1.txt', 'r') as file:
        arp_table = file.read()

    # Use regular expressions to find IP addresses and MAC addresses
    ip_mac_pairs = re.findall(r'Internet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\S+\s+(\S+)\s+ARPA\s+\S+', arp_table)

    if not ip_mac_pairs:
        print("No IP addresses and MAC addresses found in ARP table!")
        return []
    else:
        # Print and return the extracted IP addresses and MAC addresses
        print("IP Address - MAC Address\n")
        for pair in ip_mac_pairs:
            ip = pair[0]
            mac = pair[1]
            print(f"{ip} - {mac}")

        return ip_mac_pairs


def filter_management_ips(ip_mac_addresses, management_subnet):
    # Extract IP addresses from the input list of tuples
    ip_addresses = [pair[0] for pair in ip_mac_addresses]
    
    # Convert management subnet to network object
    management_network = ip_network(management_subnet, strict=False)
    
    # Filter IP addresses belonging to the management subnet
    management_ips = [(ip, mac) for ip, mac in ip_mac_addresses if ip_address(ip) in management_network]
    
    return management_ips


def normalize_mac(mac):
    # Converts various MAC address formats to a standardized form
    mac = mac.replace(':', '').replace('-', '').replace('.', '').replace(' ', '').upper()
    return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))


def update_ip_addresses(management_ips_with_mac):
    # Read the MAC addresses file
    mac_df = pd.read_excel('mac11.xlsx')

    # Display the initial DataFrame for debugging
    #print("Initial DataFrame:")
    #print(mac_df)

    # Iterate through management IPs with MAC addresses
    for ip, mac in management_ips_with_mac:
        # Normalize MAC address format for comparison
        normalized_mac = normalize_mac(mac)

        # Check if the normalized MAC address exists in the DataFrame
        mask = mac_df['VLAN MAC'].apply(normalize_mac) == normalized_mac
        if mask.any():
            # Update the corresponding IP address if MAC matches
            mac_df.loc[mask, 'IP Address'] = ip
            print(f"Updated IP address {ip} for MAC {mac}")
        else:
            print(f"No match found for MAC {mac}")

    # Display the updated DataFrame for debugging
    #print("\nUpdated DataFrame:")
    #print(mac_df)

    # Write the updated DataFrame back to the file
    mac_df.to_excel('mac11.xlsx', index=False)


def get_host_name():
    # Read the MAC addresses file
    mac_df = pd.read_excel('mac11.xlsx')

    ip_host_array = []
    for index, row in mac_df.iterrows():
        ip_address = row['IP Address']
        host_name = row['Host Name']
        status = row['Status']
        mgmt_ip = row['Management IP']
        if pd.notnull(ip_address):
            ip_host_array.append([ip_address, host_name,status,mgmt_ip])

    return ip_host_array


def config_ssh2(tuples_list):
    for ip, host, status in tuples_list:
        try:
            device = {
                'device_type': 'cisco_ios_telnet',
                'ip': ip,
                'username': 'test',
                'password': 'Kbsl@123',
                'port': 23
            }
            net_connect = ConnectHandler(**device)
            print("Connected to ",host,"-", ip, )

            output = net_connect.send_config_set(['crypto key generate rsa general-keys modulus 1024', '\n', '\n', 'ip ssh version 2'])
            print(output)

            net_connect.disconnect()
            print("Disconnected from ",host,"-", ip, )

        except Exception as e:
            print(f"Failed to connect to {ip}: {str(e)}")
            continue  # Move to the next IP even if there's an exception


def exe_commands_to_hosts2(user, password, ip_and_mac):
    for ip, host, status, mgmt_ip in ip_and_mac:
        if int(status)==0:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print('Connecting to ',host,"-", ip)
                ssh_client.connect(hostname=ip, username=user, password=password)

                shell = ssh_client.invoke_shell()

                commands = [
                'enable',
                'cisco',
                'configure terminal',
                f'hostname {host}',
                'vlan 99',
                'name Management',
                'exit',
                'int vlan 99',
                'ip address {mgmt_ip} 255.255.252.0',
                'no shutdown',
                'exit',
                'end',
                'copy running-config startup-config',
                '\n']

                for command in commands:
                    shell.send(command + '\n')
                    while not shell.recv_ready():
                        pass
                    output = shell.recv(65535).decode("utf-8")
                    # print(f"Output for command '{command}':")
                    # print(output.decode())  # Decode the bytes to string for readability
                    time.sleep(1)
                print('Succefully configured ',host,"-", ip)

                mac_df = pd.read_excel('mac11.xlsx')
                mac_df.loc[mac_df['IP Address'].isin(ip), 'Status'] = 1
                mac_df.to_excel('mac11.xlsx', index=False)
                ssh_client.close()

            except Exception as e:
                print(f"Failed to connect to {ip}: {str(e)}")
                continue  # Move to the next IP even if there's an exception

    print("Done")


######################################################################################################
## arp_table1.txt to save arp table of core switch
## mac11.xlsx to save inventory


def main():

    # Input the Cisco switch details
    switch_ip = input("Enter the Cisco switch IP address: ")
    username = 'kbsl'
    password = 'kbsl@123'

    # SSH and get ARP table
    ssh_to_core(switch_ip,username,password)

    # Get Ip 
    ip_mac_addresses = print_ip_and_mac()
    print(ip_mac_addresses)

    management_subnet = input("Enter the management subnet (e.g., 192.168.10.0/24): ")

    management_ips_with_mac = filter_management_ips(ip_mac_addresses, management_subnet)

    print(management_ips_with_mac)

    update_ip_addresses(management_ips_with_mac)

    ip_and_mac = get_host_name()
    config_ssh2(ip_and_mac)
    

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
    '\n']

    user1 = 'test'
    password1 = 'Kbsl@123'
    exe_commands_to_hosts2(user1, password1, ip_and_mac)





if __name__ == "__main__":
    main()