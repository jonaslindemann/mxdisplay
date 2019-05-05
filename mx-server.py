#!/usr/bin/env python3

import zmq

from flask import Flask, abort, redirect, url_for, render_template, request
app = Flask(__name__)

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/set_info_text', methods=['GET', 'POST'])
def set_info_text():
    if request.method == 'POST': 
        info_text = request.form.get('info_text')

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        
        print("Connecting to MX-sign server...")
        socket.connect("tcp://localhost:5555")

        socket.send_string('set_info_text')
        message = socket.recv_string()
        print("Message received: ", message)
        socket.send_string(info_text)
        message = socket.recv_string()
        print("Message received: ", message)

        socket.close()

        return redirect(url_for('start_page'))

@app.route('/set_warn_text', methods=['GET', 'POST'])
def set_warn_text():
    if request.method == 'POST': 
        warn_text = request.form.get('warn_text')

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        
        print("Connecting to MX-sign server...")
        socket.connect("tcp://localhost:5555")

        socket.send_string('set_warn_text')
        message = socket.recv_string()
        print("Message received: ", message)
        socket.send_string(warn_text)
        message = socket.recv_string()
        print("Message received: ", message)

        socket.close()

        return redirect(url_for('start_page'))

@app.route("/command/<cmd>")
def command(cmd):

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    print("Connecting to MX-sign server...")
    socket.connect("tcp://localhost:5555")

    socket.send_string(cmd)
    message = socket.recv_string()
    print("Message received: ", message)

    socket.close()

    return redirect(url_for('start_page'))