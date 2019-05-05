#!/usr/bin/env python3

import zmq

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    print("Connecting to hello world server…")
    socket.connect("tcp://localhost:5555")

    #  Socket to talk to server
    while True:
        msg = input("> ")
        print("Sent message")
        socket.send_string(msg)
        message = socket.recv_string()
        print("Message received: ", message)
