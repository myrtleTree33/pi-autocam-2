# -*- coding: utf-8 -*-

import io
import os
import picamera
import time
from threading import Thread

## Globals here
camera_id = "000"
camera_fps = 8
camera_resolution = (160,90)
camera_format = 'h264'
camera_quality = 15
camera_bitrate = 1000000

## Global objects
camera = picamera.PiCamera()

camera.resolution = camera_resolution
camera.framerate = camera_fps
camera.annotate_text_size = 10

def preview_video():
    global camera

    print 'Starting capture..'
    camera.start_preview()
    time.sleep(10)
    print 'Ending capture..'

if __name__ == '__main__':
    preview_video()
