import paramiko
import re
from ipaddress import ip_network, ip_address
 
def ssh_cisco_switch(hostname, username, password, command):
    # Create an SSH client
    client = paramiko.SSHClient()
    # Automatically add the server's host key (this is insecure and should be avoided in production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
    try:
        # Connect to the device
        client.connect(hostname, username=username, password=password, look_for_keys=False, port='22')
 
        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
 
        # Read and return the output
        return stdout.read().decode()
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {hostname}.")
    except paramiko.SSHException as e:
        print(f"SSH connection to {hostname} failed: {e}")
    except Exception as e:
        print(f"Error connecting to {hostname}: {e}")
    finally:
        # Close the SSH connection
        client.close()
 
def execute_commands_over_ssh(ip, username, password, commands):
    try:
        # SSH into the device
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, look_for_keys=False)
 
        # Execute the commands
        for command in commands:
            _, stdout, stderr = client.exec_command(command)
            error_message = stderr.read().decode().strip()
            if error_message:
                print(f"Error executing command '{command}' on {ip}: {error_message}")
 
        print(f"Commands pushed to {ip}")
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {ip}.")
    except paramiko.SSHException as e:
        print(f"SSH connection to {ip} failed: {e}")
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")
    finally:
        # Close the SSH connection
        client.close()
 
def extract_ip_addresses(arp_table_output):
    # Use regex to extract IP addresses from the ARP table output
    pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    return re.findall(pattern, arp_table_output)
 
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
 
def main():
    # Input the Cisco switch details
    switch_ip = input("Enter the Cisco switch IP address: ")
    username = 'testadmin'
    password = 'cisco'
 
    # SSH command to get ARP table
    command = 'show arp'
 
    # Fetch ARP table
    arp_table_output = ssh_cisco_switch(switch_ip, username, password, command)
 
    # Display the current ARP table
    print("Current ARP table:")
    print(arp_table_output)
 
    # Input the management subnet
    management_subnet = input("Enter the management subnet (e.g., 192.168.20.0/24): ")
 
    # Extract IP addresses from ARP table
    ip_addresses = extract_ip_addresses(arp_table_output)
 
    if not ip_addresses:
        print("No IP addresses found in ARP table!")
        return
 
    # Filter IP addresses based on management subnet
    management_ips = filter_management_ips(ip_addresses, management_subnet)
 
    if not management_ips:
        print("No management IP found!")
    else:
        # Save management IPs to a file
        save_ips_to_file(management_ips, 'management_ips.txt')
        print("\nManagement IPs saved in management_ips.txt:")
        for ip in management_ips:
            print(ip)
 
        # Execute commands over SSH on filtered IPs
        commands_to_execute = [
            'enable'
            'cisco'
            'conf t'
            #'username test2 privilege 15 password cisco'
            #'interface loopback 1'
            #'exit'
            'do show arp'
        ]
 
        # SSH into the device once and execute commands for each IP
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, username=username, password=password, look_for_keys=False)
 
            for ip in management_ips:
                print(f"\nExecuting commands on {ip}")
                # Execute the loopback interface creation commands
                execute_commands_over_ssh(ip, username, password, commands_to_execute)
 
if __name__ == "__main__":
    main()