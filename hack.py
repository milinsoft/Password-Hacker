import socket

import sys

args = sys.argv

ip_address = args[1]
port = int(args[2])
message = args[3].encode()

with socket.socket() as client_soket:
    client_soket.connect((ip_address, port))
    client_soket.send(message)
    response = client_soket.recv(1024).decode()
    print(response)

