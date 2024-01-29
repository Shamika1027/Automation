import paramiko
import time
from ipaddress import ip_network, ip_address
import pandas as pd

def get_vlan_status(ip_address, file_path):
    try:
        # Read the Excel file into a pandas DataFrame
        data = pd.read_excel(file_path)
        
        # Find the row where the IP address matches
        switch_info = data[data['IP ADDRESS'] == ip_address]
        
        if not switch_info.empty:
            # Extract VLAN status columns (CCTV, TV, TP, AP, AV, BMS, DATA, EACS, AVM, AVP)
            vlan_status = switch_info.iloc[0][['CCTV', 'TV', 'TP', 'AP', 'AV', 'BMS', 'DATA', 'EACS', 'AVM', 'AVP']].tolist()
            
            # Dictionary mapping VLAN names to status values
            vlan_names = ['CCTV', 'TV', 'TP', 'AP', 'AV', 'BMS', 'DATA', 'EACS', 'AVM', 'AVP']
            vlan_status_dict = {vlan_names[i]: vlan_status[i] for i in range(len(vlan_names))}
            
            return vlan_status_dict
        else:
            return False
    except Exception as e:
        return f"An error occurred: {e}"  

def exe_commands_to_hosts(user, password, ip, commands):
    host = "switch"
    try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print('Connecting to ',host,"-", ip)
                ssh_client.connect(hostname=ip, username=user, password=password)

                shell = ssh_client.invoke_shell()
                shell.send('enable\n')
                time.sleep(0.5)
                shell.send('cisco\n')
                time.sleep(0.5)
                shell.send('configure terminal\n')
                time.sleep(0.5)
                
                for command in commands:
                    shell.send(command + '\n')
                    while not shell.recv_ready():
                        pass
                    output = shell.recv(65535).decode("utf-8")
                    time.sleep(0.5)
                print('Succefully configured ',host,"-", ip)
                update_status_by_ip(ip,'../mac11.xlsx',1)

    except Exception as e:
        print(f"Failed to connect to {ip}: {str(e)}")
        # Move to the next IP even if there's an exception

def generate_commands(vlan_status_dict):
    #print(vlan_status_dict)
    vlans = []
    for vlan_name, status in vlan_status_dict.items():
        if status == 1:
            vlans.append(vlan_name)
    print("VLANS - ",vlans)

    all_commands = []

    for vlan in vlans:
        if vlan == 'CCTV':
            all_commands = all_commands + CCTV
        elif vlan == 'TV':
            all_commands = all_commands + TV
        elif vlan == 'TP':
            all_commands = all_commands + TP
        elif vlan == 'AP':
            all_commands = all_commands + AP
        elif vlan == 'AV':
            all_commands = all_commands + AV
        elif vlan == 'BMS':
            all_commands = all_commands + BMS
        elif vlan == 'DATA':
            all_commands = all_commands + DATA
        elif vlan == 'EACS':
            all_commands = all_commands + EACS
        elif vlan == 'AVM':
            all_commands = all_commands + AVM
        elif vlan == 'AVP':
            all_commands = all_commands + AVP
    vlans.clear()
    return all_commands

def update_status_by_ip(ip_address, file_path, status):
    try:
        # Read the Excel file into a pandas DataFrame
        data = pd.read_excel(file_path)
        
        # Update the 'Status' column based on the provided IP address
        mask = data['IP Address'] == ip_address
        if not data[mask].empty:
            data.loc[mask, 'VLAN Status'] = status  # Set status to 1 for the matching IP address
            
            # Save the updated DataFrame back to the Excel file
            data.to_excel(file_path, index=False)
            print(f"Status updated successfully for IP address: {ip_address}")
        else:
            print("IP address not found in the file")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_all_ips(file_path):
    try:
        # Read the Excel file into a pandas DataFrame
        data = pd.read_excel(file_path)
        
        # Extract all IP addresses from the 'IP ADDRESS' column
        all_ips = data['IP Address'].tolist()
        
        return all_ips
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    #SSH login for access switchs
    user1 = 'test'
    password1 = 'Kbsl@123'
    
    #Get all ip address from the master sheet
    ip_address_to_find = get_all_ips('../mac11.xlsx')
    print (ip_address_to_find)

    for ip in ip_address_to_find:
        try:
            #Get the relevent vlans for relevent ip from vlan sheet
            vlan_status_dict = get_vlan_status(ip,'vlan.xlsx')
            print("Starting vlan configuration of ",ip)
            if vlan_status_dict:
                #Generate full command list to configure all vlans
                commands = generate_commands(vlan_status_dict)
                # #Execute vlan commands to relevent ip
                exe_commands_to_hosts(user1, password1,ip, commands)
            else:
                print(ip+" dont present in the vlan.xlsx sheet")
        except Exception as e:
            print(f"Failed  {ip}: {str(e)}")
            # Move to the next IP even if there's an exception
            continue
        print("\n")

if __name__ == "__main__":

    #VLAN Commands
    CCTV = ['vlan 10','name CCTV','exit',]
    TV = ['vlan 20','name TV','exit',]
    TP = ['vlan 30','name TP','exit',]
    AP = ['vlan 40','name AP','exit',]
    AV = ['vlan 50','name AV','exit',]
    BMS = ['vlan 60','name BMS','exit',]
    DATA = ['vlan 70','name DATA','exit',]
    EACS = ['vlan 80','name EACS','exit',]
    AVM = ['vlan 90','name AVM','exit',]
    AVP = ['vlan 100','name AVP','exit',]

    main()

   
    