import socket, threading

localIP = "127.0.0.1"
localPortRecv = 20001
localPortSend = 20002
bufferSize = 102400
clients = []
threads = []

def main():
    # Create a datagram socket
    recv_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    # Bind to address and ip
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
            conn, client_address = recv_sock.accept()
            client = [[conn, client_address]]
            conn, client_address = send_sock.accept()
            client.append([conn, client_address])
            clients.append(client)
        threads.append(threading.Thread(target=handleClient, args=(1,clients[0], clients[1],)))
        threads.append(threading.Thread(target=handleClient, args=(1,clients[1], clients[0],)))
        for t in threads:
            t.start()

def handleClient(sender, recpt):
    while(True):
        # Receive bytes
        message = sender[0][0].recv(bufferSize)
        # Send to recpt
        recpt[1][0].sendall(message)

if __name__ == "__main__":
    main()