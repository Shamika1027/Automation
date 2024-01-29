import paramiko
import time

def read_file(ip, username, password, filename):
    try:
        # Create an SSH client instance
        client = paramiko.SSHClient()

        # Automatically add the server's host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device
        client.connect(ip, username=username, password=password, timeout=5)

        # Create an interactive shell
        shell = client.invoke_shell()

        # Send command to view file contents (replace <filename> with your file name)
        command = f"more {filename}\n"
        shell.send(command)

        # Receive and print the output (wait for a few seconds to receive the output)
        time.sleep(2)
        output = shell.recv(65535).decode('utf-8')
        print(output)

        # Close the shell and connection
        shell.close()
        client.close()

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as ssh_exc:
        print(f"Unable to establish SSH connection: {ssh_exc}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
device_ip = '192.168.10.3'  # Replace with your device's IP
user1 = 'test'
password1 = 'Kbsl@123'  # Replace with your password
file_to_read = 'config.text'  # Replace with the file you want to read

# Call the function to read the file
read_file(device_ip, user1, password1, file_to_read)


