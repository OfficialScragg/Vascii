#!/usr/bin/env python3

# Imports
import socket, threading

# Global variables and arrays
localIP = "0.0.0.0"
localPortRecv = 20001
localPortSend = 20002
bufferSize = 102400
clients = []
threads = []

def main():
    # Create a TCP socket
    recv_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    # Bind to address and ports
    recv_sock.bind((localIP, localPortRecv))
    recv_sock.listen(1)
    send_sock.bind((localIP, localPortSend))
    send_sock.listen(1)

    print("VASCII Server listening...")

    # Listen for incoming datagrams
    while True:
        clients = []
        threads = []
        for i in range(0,2):
            # Accept data up and down streams from a single cuser
            conn, client_address = recv_sock.accept()
            print("RECV:", client_address)
            client = [[conn, client_address]]
            conn, client_address = send_sock.accept()
            print("SEND:", client_address)
            client.append([conn, client_address])
            clients.append(client)
        # Create and start threads for handling clients
        threads.append(threading.Thread(target=handleClient, args=(clients[0], clients[1],)))
        threads.append(threading.Thread(target=handleClient, args=(clients[1], clients[0],)))
        for t in threads:
            t.start()

# Handle client frame exchange
def handleClient(sender, recpt):
    while(True):
        # Receive bytes
        message = sender[0][0].recv(bufferSize)
        # Send to recpt
        recpt[1][0].sendall(message)

if __name__ == "__main__":
    main()