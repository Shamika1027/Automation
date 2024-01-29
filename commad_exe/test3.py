import paramiko
import socket 
import sys
import time

ip_address = "192.168.20.192"
port = 22
username = "testadmin"
password = "cisco"
session = ""

def SSHConnect():
    global session
    print("\n------Attempting to connect to remote server------\n")
    session = paramiko.SSHClient() #stores ssh client as var "session"
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #adds missing policy automatically on first connection
    try:
        session.connect(ip_address, port,username,password,timeout=5)
    except socket.error:
        print("---Error! Unable to connect using supplied IP address / port - Program is now exiting...")
        sys.exit()
    except paramiko.ssh_exception.AuthenticationException:
        print("---Error! Supplied login information rejected by remote server - Program is now exiting...")
        sys.exit()

    print("Connected successfully!")
    
def conf_router():
    print("configuring router....")
    session_shell = session.invoke_shell()
    session_shell.send("config terminal")
    time.sleep(1)

    session_shell.send("banner motd c hi c")
    time.sleep(1)
    print("done")
    #session_shell.send("int gigabitEthernet1")
    #time.sleep(1)

    #session_shell.send("ip address 192.168.5.2 255.255.255.0")
    #time.sleep(1)

    
if __name__ == "__main__":
    SSHConnect()
    conf_router()
      