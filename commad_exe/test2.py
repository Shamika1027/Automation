import paramiko
import time

user = 'admin'
password = 'cisco'
#command = 'show arp'
ip = '192.168.20.192'

# ssh_client = paramiko.SSHClient()
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# print('Connecting to..')
# ssh_client.connect(hostname=ip, username=user, password=password)

# shell = ssh_client.invoke_shell()
# shell.send("enable\n")
# shell.send("cisco\n")
# shell.send("configure terminal\n")
# shell.send("no int loop 10\n")
# shell.send("end\n")
#time.sleep(1)

#output = shell.recv(65535)
#print(output)


def exe_ssh(ip, user, password,command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to.. ', ip )
    ssh_client.connect(hostname=ip, username=user, password=password)

    shell = ssh_client.invoke_shell()
    shell.send(command + '\n')
    output = shell.recv(65535)
    print(output)   


def exe_com_ssh(ip, user, password, commands):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to...', ip)
    ssh_client.connect(hostname=ip, username=user, password=password)

    shell = ssh_client.invoke_shell()
    for command in commands:
        shell.send(command + '\n')
        while not shell.recv_ready():
            pass
        output = shell.recv(65535)
        print(f"Output for command '{command}':")
        print(output.decode())  # Decode the bytes to string for readability
        time.sleep(1)

    ssh_client.close()

commands_to_execute = [
    'enable',
    'cisco',
    'configure terminal',
    'int loop 10',
    'end'
]


exe_com_ssh(ip,user,password,commands_to_execute)


#print(ssh_client.get_transport().is_active())

# print('Closing connection..')
# ssh_client.close()

