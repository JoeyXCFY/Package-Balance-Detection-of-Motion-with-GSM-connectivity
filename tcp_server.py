import socket

import time

import sys

 

HOST_IP = "140.122.79.84"

HOST_PORT = 1234

logic = 0

 

print("Starting socket: TCP...")

host_addr = (HOST_IP, HOST_PORT)

socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

 

print("TCP server listen @ %s:%d!" %(HOST_IP, HOST_PORT) )

socket_tcp.bind(host_addr)

socket_tcp.listen(1)

 

socket_con, (client_ip, client_port) = socket_tcp.accept()

print("Connection accepted from %s." %client_ip)

socket_con.send(str.encode("start"))

 

print("Receiving package...")

while True:
    data=0
    data_x=0
    data_y=0

    #try:
    if logic== 0:

        data = socket_con.recv(512)  

        data_x = int.from_bytes(data, "big")

        if data_x!=-1: 

            print("diff x: %d " %data_x)

            socket_con.send(str.encode("Y?"))

            logic= 1

            time.sleep(0.5)

            continue
    
    if logic== 1:

        data = socket_con.recv(512)  

        data_y = int.from_bytes(data, "big")

        if data_y!=-1: 

            print("diff y: %d " %data_y)

            socket_con.send(str.encode("X?"))

            logic= 0

            time.sleep(0.5)

            continue   


    #except Exception:  

        #socket_tcp.close()

        #sys.exit(1)