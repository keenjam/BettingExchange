#!/usr/bin/env python
import socket
import sys
import random


def agent(sock):
    # Message to be sent to C++
    # message = [random.randint(1, 10),random.randint(1, 10),random.randint(1, 10)]
    i = 0

    while i < 2500:
        a_converted = "Second"
        #a_converted = 'words'
        # Sending message to C++
        sock.sendall(str(a_converted))
        i += 1

def createConnection():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if(sock == -1):
        print("Socket creation failed")
        return -1

    server_address = ('localhost', 55000)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    connect = sock.connect(server_address)
    if(connect == -1):
        return -1

    agent(sock)

    sock.close()

if __name__ == "__main__":
    createConnection()
