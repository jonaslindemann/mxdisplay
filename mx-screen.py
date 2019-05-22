#!/usr/bin/env python3

from samplebase import SampleBase
from rgbmatrix import graphics
import time
from datetime import datetime
from math import *

import socket
import zmq

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class StatusDisplay:

    DM_OFF = 0
    DM_TIME_LEFT = 1
    DM_INFO_TEXT = 2
    DM_WARNING_TEXT = 3
    DM_TIME = 4
    DM_CLOSED = 5
    DM_STARTUP = 6
    DM_ONE_LAP = 7
    DM_TWO_LAP = 8
    DM_FINISH = 9
    DM_TIME_QUALIFY = 10
    DM_TIME_LEFT_20 = 11


    MX_VERSION = "1.0.1"

    def __init__(self, canvas, graphics):

        self.ip = get_ip()
        
        print(self.ip)

        self.display_mode = StatusDisplay.DM_STARTUP
        self.canvas = canvas
        self.graphics = graphics

        self.font = self.graphics.Font()
        self.font.LoadFont("fonts/7x13.bdf")

        self.large_font = self.graphics.Font()
        self.large_font.LoadFont("fonts/10x20.bdf")

        self.huge_font = self.graphics.Font()
        self.huge_font.LoadFont("fonts/Bahnschrift_large.bdf")

        self.extra_large_font = self.graphics.Font()
        self.extra_large_font.LoadFont("fonts/Bahnschrift.bdf")

        self.time_color = graphics.Color(255, 255, 255)
        self.time_warning_color = graphics.Color(255, 255, 0)
        self.info_color = graphics.Color(255, 255, 255)
        self.info_background = graphics.Color(0, 0, 140)
        self.warn_color = graphics.Color(0, 0, 0)
        self.warn_background = graphics.Color(200, 200, 0)
        self.warn_border = graphics.Color(200, 0, 0)
        self.time_over_color = graphics.Color(255, 0, 0)
        self.training_back = graphics.Color(128, 0, 0)
        self.training_bar = graphics.Color(0, 255, 0)      
        self.training_text = graphics.Color(0, 0, 0)  
        self.white = graphics.Color(230,230,230)
        self.black = graphics.Color(0,0,0)

        self.hour_color = graphics.Color(255,0,0)    
        self.minute_color = graphics.Color(0,255,0)
        self.second_color = graphics.Color(0,0,255)

        self.info_text = "Infotext"
        self.warning_text = "Varningstext"
        
    def draw_filled_rect(self, x0, y0, x1, y1, color):
        for y in range(y0,y1+1):
            self.graphics.DrawLine(self.canvas, x0, y, x1, y, color)
        
    def draw_rect(self, x0, y0, x1, y1, color):
        self.graphics.DrawLine(self.canvas, x0, y0, x1, y0, color)
        self.graphics.DrawLine(self.canvas, x0, y1, x1, y1, color)
        self.graphics.DrawLine(self.canvas, x0, y0, x0, y1, color)
        self.graphics.DrawLine(self.canvas, x1, y0, x1, y1, color)

    def draw_time_left(self, text, value):
        self.draw_filled_rect(64, 0, 127, 31, self.training_back)
        self.draw_filled_rect(64, 0, 64+value, 31, self.training_bar)
        self.graphics.DrawText(self.canvas, self.font, 64+2, 12, self.training_text, text)
        self.graphics.DrawText(self.canvas, self.font, 64+2, 31, self.training_text, str(value))
        
    def draw_time(self):
        self.draw_rect(0, 0, 127, 31, self.time_color)
        self.draw_rect(1, 1, 126, 30, self.time_color)
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.graphics.DrawText(self.canvas, self.extra_large_font, 6, 28, self.time_color, time_str)
        
    def draw_half_hour(self):
        #self.draw_rect(0, 0, 63, 31, self.time_color)
        now = datetime.now()
        
        minute = now.minute
        if minute <= 30:
            left_minutes = 30 - minute
        else:
            left_minutes = 60 - minute
            
        #print(minute, now.second)
        
        left_seconds = 59-now.second
        #if left_seconds == 60:
        #    left_seconds = 0
                
        time_str = "%02i:%02i" % (left_minutes, left_seconds)

        seconds_left = left_minutes*60.0 + left_seconds

        if left_minutes > 1:
            self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_color, time_str)
        else:
            if now.second % 2 == 0:
                self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_color, time_str)
            else:
                self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_over_color, time_str)

    def draw_twenty_minutes(self):
        #self.draw_rect(0, 0, 63, 31, self.time_color)
        now = datetime.now()
        
        minute = now.minute
        if minute <= 20:
            left_minutes = 20 - minute
        elif minute <= 40:
            left_minutes = 40 - minute
        else:
            left_minutes = 60 - minute
            
        #print(minute, now.second)
        
        left_seconds = 59-now.second
        #if left_seconds == 60:
        #    left_seconds = 0
                
        time_str = "%02i:%02i" % (left_minutes, left_seconds)

        seconds_left = left_minutes*60.0 + left_seconds

        if left_minutes > 1:
            self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_color, time_str)
        else:
            if now.second % 2 == 0:
                self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_color, time_str)
            else:
                self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_over_color, time_str)

    def draw_line_angular(self, x0, y0, r, angle, color):
        x1 = x0 + r*cos(angle)
        y1 = y0 + r*sin(angle)

        self.graphics.DrawLine(self.canvas, x0, y0, x1, y1, color)

    def draw_clock(self):

        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        x0 = 32*3+19
        y0 = 12

        self.graphics.DrawCircle(self.canvas, x0, y0, 12, self.time_color)
        self.graphics.DrawCircle(self.canvas, x0, y0+1, 12, self.time_color)

        hour_angle = (hour+minute/60)*2.0*pi/12.0 - 0.5*pi
        minute_angle = minute*2.0*pi/60.0 - 0.5*pi
        second_angle = second*2.0*pi/60.0 - 0.5*pi

        #print(hour_angle*360/2/pi, minute_angle*360/2/pi)

        self.draw_line_angular(x0, y0, 10, second_angle, self.second_color)
        self.draw_line_angular(x0, y0, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0, y0+1, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0+1, y0, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0, y0, 8, hour_angle, self.hour_color)
        self.draw_line_angular(x0, y0+1, 8, hour_angle, self.hour_color)
        self.draw_line_angular(x0+1, y0, 8, hour_angle, self.hour_color)

        #graphics.DrawCircle(self.canvas, 32*3+19, 12, 11, self.time_color)


    def draw_time_date(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%y-%m-%d")
        self.graphics.DrawText(self.canvas, self.font, 0, 12, self.time_color, time_str)
        self.graphics.DrawText(self.canvas, self.font, 0, 31, self.time_color, date_str)

    def draw_info_text(self):
        self.draw_filled_rect(0, 0, 127, 31, self.info_background)
        self.draw_rect(0, 0, 127, 31, self.info_color)
        self.draw_rect(1, 1, 126, 30, self.info_color)
        self.graphics.DrawText(self.canvas, self.extra_large_font, 6, 28, self.info_color, self.info_text)
    
    def draw_warn_text(self):
        self.draw_filled_rect(0, 0, 127, 31, self.warn_background)
        self.draw_rect(0, 0, 127, 31, self.warn_border)
        self.draw_rect(1, 1, 126, 30, self.warn_border)
        self.graphics.DrawText(self.canvas, self.extra_large_font, 6, 28, self.warn_color, self.warning_text)

    def draw_startup(self):
        self.ip = get_ip()
        self.graphics.DrawText(self.canvas, self.font, 4, 11, self.time_color, self.ip+":5000")
        self.graphics.DrawText(self.canvas, self.font, 4, 30, self.time_color, "mxdisplay-"+self.MX_VERSION)

    def draw_lap_left(self, laps_left, offset):
        self.draw_filled_rect(0, 0, 127, 31, self.white)
        self.graphics.DrawText(self.canvas, self.extra_large_font, 20+offset, 28, self.black, str(laps_left)+" VARV")

    def draw_time_qualify(self):
        self.graphics.DrawText(self.canvas, self.extra_large_font, 10, 28, self.white, "Tidskval")

    def draw_finish(self):
        offset = 0
        for y in range(32):
            if y % 4 == 0:
                if offset == 0:
                    offset = 4
                else:
                    offset = 0

            for x in range(0,128,8):
                self.graphics.DrawLine(self.canvas, x+offset, y, x+3+offset, y, self.white)

    def draw(self):
        if self.display_mode == StatusDisplay.DM_TIME_LEFT:
            self.draw_half_hour()
            self.draw_clock()
        elif self.display_mode == StatusDisplay.DM_TIME_LEFT_20:
            self.draw_twenty_minutes()
            self.draw_clock()
        elif self.display_mode == StatusDisplay.DM_CLOSED:
            pass
        elif self.display_mode == StatusDisplay.DM_TIME:
            self.draw_time()
        elif self.display_mode == StatusDisplay.DM_INFO_TEXT:
            self.draw_info_text()
        elif self.display_mode == StatusDisplay.DM_WARNING_TEXT:
            self.draw_warn_text()
        elif self.display_mode == StatusDisplay.DM_STARTUP:
            self.draw_startup()
        elif self.display_mode == StatusDisplay.DM_OFF:
            pass
        elif self.display_mode == StatusDisplay.DM_ONE_LAP:
            self.draw_lap_left(1, 0)
        elif self.display_mode == StatusDisplay.DM_TWO_LAP:
            self.draw_lap_left(2, -3)
        elif self.display_mode == StatusDisplay.DM_FINISH:
            self.draw_finish()
        elif self.display_mode == StatusDisplay.DM_TIME_QUALIFY:
            self.draw_time_qualify()

class MxDisplay(SampleBase):
    def __init__(self, *args, **kwargs):
        super(MxDisplay, self).__init__(*args, **kwargs)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        
        status_display = StatusDisplay(offscreen_canvas, graphics)
        status_display.display_mode = StatusDisplay.DM_STARTUP

        while True:

            try:
                message = self.socket.recv_string(flags=zmq.NOBLOCK)
                print("Message received: ", message)

                if message == "time_left":
                    print("Switching to DM_TIME_LEFT")
                    status_display.display_mode = StatusDisplay.DM_TIME_LEFT
                elif message == "time_left_twenty":
                    print("Switching to DM_TIME_LEFT")
                    status_display.display_mode = StatusDisplay.DM_TIME_LEFT_20
                elif message == "time":
                    print("Switching to DM_TIME")
                    status_display.display_mode = StatusDisplay.DM_TIME
                elif message == "off":
                    print("Switching to DM_OFF")
                    status_display.display_mode = StatusDisplay.DM_OFF
                elif message == "info":
                    print("Switchiong to DM_INFO_TEXT")
                    status_display.display_mode = StatusDisplay.DM_INFO_TEXT
                elif message == "warn":
                    print("Switchiong to DM_WARNING_TEXT")
                    status_display.display_mode = StatusDisplay.DM_WARNING_TEXT
                elif message == "one_lap":
                    print("Switching to DM_ONE_LAP")
                    status_display.display_mode = StatusDisplay.DM_ONE_LAP
                elif message == "two_lap":
                    print("Switching to DM_TWO_LAP")
                    status_display.display_mode = StatusDisplay.DM_TWO_LAP
                elif message == "finish":
                    print("Switching to DM_FINISH")
                    status_display.display_mode = StatusDisplay.DM_FINISH
                elif message == "qualify":
                    print("Switching to DM_TIME_QUALIFY")
                    status_display.display_mode = StatusDisplay.DM_TIME_QUALIFY
                elif message == "startup":
                    print("Switching to DM_STARTUP")
                    status_display.display_mode = StatusDisplay.DM_STARTUP
                elif message == "set_info_text":
                    print("set_info_text:")
                    self.socket.send_string("OK")
                    text = self.socket.recv_string()
                    print("Text received: ", text)
                    status_display.info_text = text
                    status_display.display_mode = StatusDisplay.DM_INFO_TEXT
                elif message == "set_warn_text":
                    print("Setting warn_text")
                    self.socket.send_string("OK")
                    text = self.socket.recv_string()
                    print("Text received: ", text)
                    status_display.warning_text = text
                    status_display.display_mode = StatusDisplay.DM_WARNING_TEXT

                self.socket.send_string("OK")
            except zmq.Again as e:
                pass

            offscreen_canvas.Clear()
            
            status_display.canvas = offscreen_canvas
            status_display.draw()
            
            time.sleep(0.1)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            
            
# Main function
if __name__ == "__main__":

    mx_display = MxDisplay()
    if (not mx_display.process()):
        mx_display.print_help()

