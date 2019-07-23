#!/usr/bin/env python3
"""
Status display socket server

This module implements the control logic of the LED display. Control
of the display is implemented as a simple socket server implemented 
using ZeroMQ.
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

from samplebase import SampleBase
from rgbmatrix import graphics
from datetime import datetime
from math import *

import time
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
    """Main class implementing the control of the LED display"""

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
    DM_TIMING = 12

    MX_VERSION = "1.0.3"

    def __init__(self, canvas, graphics):
        """Class constructor"""

        self.ip = get_ip()
        
        print(self.ip)

        self._display_mode = StatusDisplay.DM_STARTUP
        self.default_mode = StatusDisplay.DM_TIME_LEFT
        self.canvas = canvas
        self.graphics = graphics

        self.elapsed_time = 0.0
        self.startup_delay = 60
        self.startup_finished = False

        self.timing_start = datetime.now()

        self.font = self.graphics.Font()
        self.font.LoadFont("fonts/7x13.bdf")

        self.large_font = self.graphics.Font()
        self.large_font.LoadFont("fonts/9x18B.bdf")

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
        """Draws a filled rectangle in the LED display"""

        for y in range(y0,y1+1):
            self.graphics.DrawLine(self.canvas, x0, y, x1, y, color)
        
    def draw_rect(self, x0, y0, x1, y1, color):
        """Draw a rectangle in the LED display"""

        self.graphics.DrawLine(self.canvas, x0, y0, x1, y0, color)
        self.graphics.DrawLine(self.canvas, x0, y1, x1, y1, color)
        self.graphics.DrawLine(self.canvas, x0, y0, x0, y1, color)
        self.graphics.DrawLine(self.canvas, x1, y0, x1, y1, color)

    def draw_time_left(self, text, value):
        """Draw time left as a bar"""

        self.draw_filled_rect(64, 0, 127, 31, self.training_back)
        self.draw_filled_rect(64, 0, 64+value, 31, self.training_bar)
        self.graphics.DrawText(self.canvas, self.font, 64+2, 12, self.training_text, text)
        self.graphics.DrawText(self.canvas, self.font, 64+2, 31, self.training_text, str(value))
        
    def draw_time(self):
        """Draw current time in the LED display"""

        self.draw_rect(0, 0, 127, 31, self.time_color)
        self.draw_rect(1, 1, 126, 30, self.time_color)
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.graphics.DrawText(self.canvas, self.extra_large_font, 6, 28, self.time_color, time_str)
        
    def draw_half_hour(self):
        """Draw time left in half-hour practice sessions."""

        now = datetime.now()
        
        minute = now.minute
        if minute <= 30:
            left_minutes = 30 - minute
        else:
            left_minutes = 60 - minute
            
        
        left_seconds = 59-now.second
                
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
        """Draw time left in 20-minute practice sessions."""

        now = datetime.now()
        
        minute = now.minute
        if minute <= 20:
            left_minutes = 20 - minute
        elif minute <= 40:
            left_minutes = 40 - minute
        else:
            left_minutes = 60 - minute
                  
        left_seconds = 59-now.second
                
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
        """Draw angular line in LED display"""
        x1 = x0 + r*cos(angle)
        y1 = y0 + r*sin(angle)

        self.graphics.DrawLine(self.canvas, x0, y0, x1, y1, color)

    def draw_clock(self):
        """Draw analog clock in LED display."""

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

        self.draw_line_angular(x0, y0, 10, second_angle, self.second_color)
        self.draw_line_angular(x0, y0, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0, y0+1, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0+1, y0, 10, minute_angle, self.minute_color)
        self.draw_line_angular(x0, y0, 8, hour_angle, self.hour_color)
        self.draw_line_angular(x0, y0+1, 8, hour_angle, self.hour_color)
        self.draw_line_angular(x0+1, y0, 8, hour_angle, self.hour_color)

    def draw_timing(self):
        """Draw time since start of timing."""

        now = datetime.now()

        elapsed_time = now - self.timing_start

        seconds = elapsed_time.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60        
                      
        time_str = "%02i:%02i" % (minutes, seconds)

        self.graphics.DrawText(self.canvas, self.huge_font, 0, 32, self.time_color, time_str)

    def draw_time_date(self):
        """Draw time and date in the LED display."""

        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%y-%m-%d")
        self.graphics.DrawText(self.canvas, self.font, 0, 12, self.time_color, time_str)
        self.graphics.DrawText(self.canvas, self.font, 0, 31, self.time_color, date_str)

    def draw_info_text(self):
        """Draw information text."""

        self.draw_filled_rect(0, 0, 127, 31, self.info_background)
        self.graphics.DrawText(self.canvas, self.large_font, 10, 22, self.info_color, self.info_text)
        self.draw_rect(0, 0, 127, 31, self.info_color)
        self.draw_rect(1, 1, 126, 30, self.info_color)
    
    def draw_warn_text(self):
        """Draw warning text"""

        self.draw_filled_rect(0, 0, 127, 31, self.warn_background)
        self.graphics.DrawText(self.canvas, self.large_font, 10, 22, self.warn_color, self.warning_text)
        self.draw_rect(0, 0, 127, 31, self.warn_border)
        self.draw_rect(1, 1, 126, 30, self.warn_border)

    def draw_startup(self):
        """Draw startup screen with ip and version."""

        self.ip = get_ip()
        self.graphics.DrawText(self.canvas, self.font, 4, 11, self.time_color, self.ip+":5000")
        self.graphics.DrawText(self.canvas, self.font, 4, 30, self.time_color, "mxdisplay-"+self.MX_VERSION)

    def draw_lap_left(self, laps_left, offset):
        """Draw laps left sign"""
        self.draw_filled_rect(0, 0, 127, 31, self.white)
        self.graphics.DrawText(self.canvas, self.extra_large_font, 20+offset, 28, self.black, str(laps_left)+" VARV")

    def draw_time_qualify(self):
        """Draw time qualify in sign"""

        self.graphics.DrawText(self.canvas, self.extra_large_font, 10, 28, self.white, "Tidskval")

    def draw_finish(self, invert=False):
        """Draw finish flag"""
        
        if invert:
            offset = 8
        else:
            offset = 0

        sq_size = 8
        for y in range(32):
            if y % sq_size == 0:
                if offset == 0:
                    offset = sq_size
                else:
                    offset = 0

            for x in range(0,128,sq_size*2):
                self.graphics.DrawLine(self.canvas, x+offset, y, x+(sq_size-1)+offset, y, self.white)

    def draw(self):
        """Main draw routine of the display."""
        
        if self._display_mode == StatusDisplay.DM_TIME_LEFT:
            self.draw_half_hour()
            self.draw_clock()
        elif self._display_mode == StatusDisplay.DM_TIME_LEFT_20:
            self.draw_twenty_minutes()
            self.draw_clock()
        elif self._display_mode == StatusDisplay.DM_CLOSED:
            pass
        elif self._display_mode == StatusDisplay.DM_TIME:
            self.draw_time()
        elif self._display_mode == StatusDisplay.DM_INFO_TEXT:
            self.draw_info_text()
        elif self._display_mode == StatusDisplay.DM_WARNING_TEXT:
            self.draw_warn_text()
        elif self._display_mode == StatusDisplay.DM_STARTUP:
            self.draw_startup()
        elif self._display_mode == StatusDisplay.DM_OFF:
            pass
        elif self._display_mode == StatusDisplay.DM_ONE_LAP:
            self.draw_lap_left(1, 0)
        elif self._display_mode == StatusDisplay.DM_TWO_LAP:
            self.draw_lap_left(2, -3)
        elif self._display_mode == StatusDisplay.DM_FINISH:
            now = datetime.now()
            if now.second % 2 == 0:
                self.draw_finish(True)
            else:
                self.draw_finish(False)
        elif self._display_mode == StatusDisplay.DM_TIME_QUALIFY:
            self.draw_time_qualify()
        elif self._display_mode == StatusDisplay.DM_TIMING:
            self.draw_timing()

    def reset_timing(self):
        """Reset timing to zero."""

        self.timing_start = datetime.now()

    def set_display_mode(self, mode):
        """Display mode setter"""

        self._display_mode = mode

    def get_display_mode(self):
        """Display mode getter"""
        return self._display_mode

    display_mode = property(get_display_mode, set_display_mode)

class MxDisplay(SampleBase):
    """Class implementing the display server"""

    def __init__(self, *args, **kwargs):
        """Class constructor"""
        
        super(MxDisplay, self).__init__(*args, **kwargs)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")

    def run(self):
        """Main run loop of the server."""

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        
        status_display = StatusDisplay(offscreen_canvas, graphics)
        status_display.display_mode = StatusDisplay.DM_STARTUP

        while True:

            try:
                message = self.socket.recv_string(flags=zmq.NOBLOCK)
                print("Message received: ", message)

                status_display.startup_finished = True                

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
                elif message == "timing":
                    print("Switching to DM_TIMING")
                    status_display.display_mode = StatusDisplay.DM_TIMING
                elif message == "reset_timing":
                    print("Resetting timing")
                    status_display.reset_timing()
                    status_display.display_mode = StatusDisplay.DM_TIMING

                self.socket.send_string("OK")
            except zmq.Again as e:
                pass

            offscreen_canvas.Clear()
            
            status_display.canvas = offscreen_canvas
            status_display.draw()

            # Check if startup delay is completed and switch
            # to default mode
            
            if (status_display.elapsed_time > status_display.startup_delay) and not status_display.startup_finished:
               status_display.startup_finished = True 
               status_display.display_mode = status_display.default_mode
            
            time.sleep(0.1)
            status_display.elapsed_time += 0.1

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            
            
# Main function
if __name__ == "__main__":

    mx_display = MxDisplay()
    if (not mx_display.process()):
        mx_display.print_help()

