import re
from ipaddress import ip_network, ip_address

# Read the contents of the file
with open('arp_table.txt', 'r') as file:
    arp_table = file.read()

# Use regular expressions to find IP addresses
ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', arp_table)

# # Print the extracted IP addresses
# for ip in ip_addresses:
#     print(ip)

def filter_management_ips(ip_addresses, management_subnet):
    # Convert management subnet to network object
    management_network = ip_network(management_subnet, strict=False)
 
    # Filter IP addresses belonging to the management subnet
    management_ips = [ip for ip in ip_addresses if ip_address(ip) in management_network]
 
    return management_ips

# Input the management IP range
management_subnet = '192.168.20.0/24'  # Example management subnet

# Filter IP addresses within the management subnet
management_ips = filter_management_ips(ip_addresses, management_subnet)

# Print the filtered management IPs
for ip in management_ips:
    print(ip)
