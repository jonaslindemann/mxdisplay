# Status display for Motocross activities

This project aims to provide a simple way of driving a 128 x 32 LED sign for use in motocross competitons and practice. 

The code uses the libraries from the rpi-rgb-led-matrix-project on github:

https://github.com/hzeller/rpi-rgb-led-matrix

The project consists of 2 parts:

 * Display-server (mx-screen.py) driving the LED panel. It uses the ZeroMQ library to implement a simple socket-server listening for commands from a client application.
 * Web-server (mx-server.py) implemented using Flask acting as the client application. Issues commands to the Display-server.
 
# Parts list

You will need the following hardware to implement the sign:

 * Raspberry Pi 3/4 with 16 GB SD card.
 * RGB Matrix Bonnet - https://www.adafruit.com/product/3211
 * 4 32x32 LED Matrices - https://www.adafruit.com/product/1484 (or equivalent)
 * Powersupply - https://www.kjell.com/se/produkter/el-verktyg/stromforsorjning/nataggregat/ac-dc/fast-utspanning/mean-well-switchat-nataggregat-5-v-(dc)-90-w-p44815
 * Casing of own design.
 
# Example of installation

![Example of a completed sign](https://github.com/jonaslindemann/mxdisplay/blob/master/images/mxsign1.jpg)

# Installation

1. Install and build the rpi-rgb-led-matrix library
2. Install Flask (Flask)
3. Install ZeroMQ (pyzmq)

## Installing services:

From the source directory:

  sudo cp mx-screen.service /etc/systemd/system/mx-screen.service
  sudo cp mx-web.service /etc/systemd/system/mx-web.service
  sudo systemctl daemon-reload
  sudo systemctl enable mx-screen.service
  sudo systemctl enable mx-web.service
  sudo systemctl start mx-screen
  sudo systemctl start mx-web
  
This should make the display- and web-server start automatically at reboot

At startup the system will display its ip- and port number for 30-seconds in the display.

# Security

PLEASE NOTE: There is no security. The web-server is non-authenticated. The display-server only listens to localhost. The project is meant to be run in a controlled environment.

  



