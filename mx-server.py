#!/usr/bin/env python3
"""
Status display web server

This module implements a flask web-server for controlling the display. 
"""

#
# Copyright 2019 Jonas Lindemann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import zmq

from flask import Flask, abort, redirect, url_for, render_template, request
app = Flask(__name__)

@app.route('/')
def start_page():
    """Render server start page."""

    return render_template('index.html')

@app.route('/set_info_text', methods=['GET', 'POST'])
def set_info_text():
    """Handle the set_info_text request."""

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

        return render_template('index.html')
    else:
        return render_template('index.html')
        

@app.route('/set_warn_text', methods=['GET', 'POST'])
def set_warn_text():
    """Handle the set_warn_text request"""

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

        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route("/command/<cmd>")
def command(cmd):
    """Redirect other request to socket server."""

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    print("Connecting to MX-sign server...")
    socket.connect("tcp://localhost:5555")

    socket.send_string(cmd)
    message = socket.recv_string()
    print("Message received: ", message)

    socket.close()

    return redirect(url_for('start_page'))