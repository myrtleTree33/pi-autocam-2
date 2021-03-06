# -*- coding: utf-8 -*-

"""
Author: Joel Haowen TONG
Description: Deploys Raspberry Pi and camera as a security camera unit.

Features:
- Records in H264 format
- Ability to remove older videos exceeding specified lifetime
- Able to both display live video feed while recording H264
- Able to view live video feed at http://localhost:5000
- Able to timestamp and show camera ID stamps on video

Github: https://github.com/myrtleTree33/pi-autocam-2
"""

import io
import click
import os
import collections
import picamera
import time
from threading import Thread
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask, render_template, Response

## VERSION NUMBER
VERSION_NUMBER = '1.0.2'
## / VERSION NUMBER


class BufferedImage(object):
    """
    Queue data structure that ensures
    image is not corrupted when writing or
    reading.  This is done by ensuring an
    image is always in the queue pipeline.
    """
    def __init__(self, size):
        self.q = collections.deque()
        self.size = size


    def put(self, image_obj):
        while len(self.q) >= self.size:
            img = self.q.popleft()
            img.close()
        self.q.append(image_obj)


    def get(self):
        if len(self.q) == 0:
            return None
        return self.q[0]


class ForkedOutput(object):
    """
    This is a custom output that can
    be used for forking data, to be
    used elsewhere.
    """
    def __init__(self, file_name):
        self.file = io.open(file_name, 'wb')

    def write(self, buff):
        self.file.write(buff)

    def flush(self):
        self.file.flush()

    def close(self):
        pass


## Constants here
STARTING_CAPTURE_STRING = 'Starting capture..'
ENDING_CAPTURE_STRING = 'Ending capture..'
CAMERA_DONE_TEXT = 'Done!'
CAMERA_TEXT_SIZE = 14

## Rough measurements from screen
CAMERA_TEXT_AVERAGE_WIDTH = 7
CAMERA_TEXT_NEWLINE_HEIGHT = 11
CAMERA_TEXT_SPACE_WIDTH = CAMERA_TEXT_AVERAGE_WIDTH

GARBAGE_CHECK_TIME_SECS = 10
BUFFERED_IMAGE_MAX_BUFFER_SIZE = 2
## / Constants here

## Global default command parameters here
camera_id = "000"
camera_fps = 8
camera_resolution = (160,90)
camera_format = 'h264'
camera_quality = 15
camera_bitrate = 1000000
camera_start = (8, 0)
camera_end = (19, 0)
camera_time_diff = -1
file_life_span = 60 * 60 * 24 * 10   # 10 days
recording_directory = './rec/'
## / Global default command parameters here

## Global objects
camera = picamera.PiCamera()
sched = BlockingScheduler()
output = None
image_stream = BufferedImage(BUFFERED_IMAGE_MAX_BUFFER_SIZE)

running = True
## / Global objects


def get_timestamp():
    return '#' + camera_id + '_' + str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))


def make_recording_text(text):
    """
    This function positions text at top right corner
    by adding spaces to text.
    """
    avail_left_spaces = camera_resolution[0] / CAMERA_TEXT_AVERAGE_WIDTH
    left = ' ' * (avail_left_spaces - len(text) - 5)
    return left + text


def take_video(duration):
    global running
    global camera
    global recording_directory
    global output
    global image_stream
    time_start = datetime.now()

    print STARTING_CAPTURE_STRING
    recording_name = recording_directory + get_timestamp() + '.h264'
    output = ForkedOutput(recording_name)

    camera.start_recording(output, format=camera_format, quality=camera_quality, bitrate=camera_bitrate, splitter_port=1)

    ## Enable for live preview in terminal
    camera.start_preview(fullscreen=False, window=(50,50,160,90))

    ## This hack takes a photo in between video snapshots,
    ## using the video port, such that is is barely discernible.
    while (datetime.now() - time_start).seconds < duration:
        camera.wait_recording(0.1)
        stream = io.BytesIO()
        camera.capture(stream, use_video_port=True, format='jpeg')
        image_stream.put(stream)
    camera.stop_recording()
    output.close()
    print ENDING_CAPTURE_STRING
    running = False


def make_timestamp():
    global running
    global camera
    while running:
        camera.annotate_text = make_recording_text(get_timestamp())
        time.sleep(0.001)


@click.command()
@click.option('--fps', default=2, help='Frames per second to record')
@click.option('--width', default=160, help='The screen capture width')
@click.option('--height', default=90, help='The screen capture height')
@click.option('--bitrate', default=1000000, help='The maximum video bitrate to use.  To capture more colors, set a higher bitrate setting.')
@click.option('--start', default='0700', help='Video start time, in 4-digit military time')
@click.option('--end', default='1800', help='Video end time, in 4-digit military time')
@click.option('--id', default='000', help='Camera ID')
@click.option('--filelifespan', default=60 * 60 * 24 * 10, help='Maximum lifespan of each file in seconds, before file is deleted.')
@click.option('--recorddir', default='./rec/', help='The directory to store recordings to')
def prog(fps, width, height, bitrate, start, end, id, filelifespan, recorddir):
    """
    Program to turn Raspberry Pi into a security camera, with live streaming.

    Stream available at http://localhost:5000
    """

    print 'Running version ' + VERSION_NUMBER + '.'

    def calc_time_diff(startTuple, endTuple):
        """
        Retrieves the number of seconds between 2 time tuples
        """
        print startTuple, endTuple
        start = datetime(year=2014, month=2, day=14, hour=startTuple[0], minute=startTuple[1])
        end = datetime(year=2014, month=2, day=14, hour=endTuple[0], minute=endTuple[1])
        secs = (end - start).total_seconds()
        print('Running for %d secs..' % (secs))
        return secs

    global camera_fps
    global camera_resolution
    global camera_bitrate
    global camera_start
    global camera_end
    global camera_time_diff
    global camera_id
    global file_life_span
    global recording_directory

    camera_fps = fps
    camera_resolution = (width, height)
    camera_bitrate = bitrate
    camera_start = (int(start[:2]), int(start[2:]))
    camera_end = (int(end[:2]), int(end[2:]))
    camera_time_diff = calc_time_diff(camera_start, camera_end)
    camera_id = str(id)
    file_life_span = filelifespan
    recording_directory = recorddir
    # check for proper delimiter
    if recording_directory[-1] != '/':
        recording_directory = recording_directory + '/'

    def perform_checks():
        def check_fps():
            if (camera_fps < 2):
                raise ValueError('FPS is too low.  Please choose a higher FPS.')
                sys.exit(-1)

        def check_aspect_ratio():
            if (float(16) / 9) != (float(width) / height):
                raise ValueError('Aspect ratio not in 16:9.  Please set accordingly.')
                sys.exit(-1)

        def check_time_diff():
            if (camera_time_diff < 0):
                raise ValueError('EndTime is earlier than StartTime.  Please correct!')
                sys.exit(-1)

        check_fps()
        check_aspect_ratio()
        check_time_diff()

    def init_camera():
        global camera
        camera.resolution = camera_resolution
        camera.framerate = camera_fps
        camera.annotate_text_size = CAMERA_TEXT_SIZE

    ## Do the necessary initializations -------
    perform_checks()
    init_camera()
    ## ----------------------------------------

    ## Run the daemons ------------------------
    init_garbage_daemon(recording_directory, file_life_span, GARBAGE_CHECK_TIME_SECS)
    init_server()
    init_camera_daemon()
    ## ----------------------------------------


def init_garbage_daemon(folder, lifespan_secs, interval_secs):
    """
    Initializes the garbage daemon
    """
    def clear_old_files(folder, lifespan_secs):
        """
        Removes old files that are no longer used.
        """
        now = time.time()
        for root, dirs, files in os.walk(folder):
            for f in files:
                long_file_path = os.path.join(root, f)
                if now - os.stat(long_file_path).st_mtime > lifespan_secs:
                    print 'Removing file ' + f + '..'
                    os.remove(long_file_path)

    def garbage_daemon(folder, lifespan_secs, interval_secs):
        while True:
            clear_old_files(folder, lifespan_secs)
            time.sleep(interval_secs)

    thread = Thread(target=garbage_daemon, args=(folder, lifespan_secs, interval_secs))
    print 'Garbage daemon running..'
    thread.start()


def run_video_job(duration):
    thread_video = Thread(target=take_video, args=(duration,))
    thread_timestamp = Thread(target=make_timestamp)

    thread_video.start()
    thread_timestamp.start()
    thread_timestamp.join()

    print CAMERA_DONE_TEXT + ' ('+ get_timestamp() + ')'


def init_camera_daemon():
    # runs scheduled capture from starttime to endtime daily
    print camera_start

    job = sched.add_job(run_video_job, 'cron', hour=int(camera_start[0]), minute=int(camera_start[1]), args=[camera_time_diff])
    sched.start()

    ## run_video_job(5) # run for 5 secs


def server():
    global output, image_stream
    print 'Live-preview server running..'
    app = Flask(__name__)

    def grab_frame(output_obj):
       while True:
           frame = image_stream.get().getvalue()
           yield(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/')
    def index():
        print 'triggered'
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(grab_frame(output), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host='0.0.0.0', threaded=True)


def init_server():
    thread_server = Thread(target=server)
    thread_server.start()


if __name__ == '__main__':
    prog()
