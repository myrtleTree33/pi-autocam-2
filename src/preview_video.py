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
camera.annotate_text_size = CAMERA_TEXT_SIZE

def preview_video():
    global camera

    print 'Starting capture..'
    recording_name = recording_directory + get_timestamp() + '.h264'
    camera.start_preview()
    print 'Ending capture..'

if __name__ == '__main__':
    preview_video()
