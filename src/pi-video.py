# -*- coding: utf-8 -*-

import click
import os
import picamera
import time
from threading import Thread
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

## Constants here
CAMERA_DONE_TEXT = 'Done!'
CAMERA_TEXT_SIZE = 6
GARBAGE_CHECK_TIME_SECS = 10

## Globals here
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

## Global objects
camera = picamera.PiCamera()
sched = BlockingScheduler()


camera.resolution = camera_resolution
camera.framerate = camera_fps
camera.annotate_text_size = CAMERA_TEXT_SIZE

running = True


def get_timestamp():
    return '#' + camera_id + '_' + str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))


def take_video():
    global running
    global camera
    print 'Starting capture..'
    camera.start_recording(get_timestamp() + '.h264', format=camera_format, quality=camera_quality, bitrate=camera_bitrate)
    camera.wait_recording(camera_time_diff)
    camera.stop_recording()
    print 'Ending capture..'
    running = False


def make_timestamp():
    global running
    global camera
    while running:
        camera.annotate_text = get_timestamp()
        time.sleep(0.001)


@click.command()
@click.option('--fps', default=2, help='Frames per second/')
@click.option('--width', default=160, help='The screen capture width')
@click.option('--height', default=90, help='The screen capture height')
@click.option('--bitrate', default=1000000, help='The maximum video bitrate to use')
@click.option('--start', default='0700', help='Video start time')
@click.option('--end', default='1800', help='Video end time')
@click.option('--id', default='000', help='Camera ID')
@click.option('--filelifespan', default=60 * 60 * 24 * 10, help='Maximum lifespan of each file')
@click.option('--recorddir', default='./rec/', help='The directory to store recordings to')
def prog(fps, width, height, bitrate, start, end, id, filelifespan, recorddir):
    """
    Simple program to take pictures
    """

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
    global file_life_span
    global recording_directory

    camera_fps = fps
    camera_resolution = (width, height)
    camera_bitrate = bitrate
    camera_start = (int(start[:2]), int(start[2:]))
    camera_end = (int(end[:2]), int(end[2:]))
    camera_time_diff = calc_time_diff(camera_start, camera_end)
    file_life_span = filelifespan
    recording_directory = recorddir

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

    perform_checks()

    ## Run the daemons ----------
    print file_life_span
    print GARBAGE_CHECK_TIME_SECS
    init_garbage_daemon(recording_directory, file_life_span, GARBAGE_CHECK_TIME_SECS)
    init_camera_daemon()
    ## --------------------------


def init_garbage_daemon(folder, lifespan_secs, interval_secs):
    """
    Initializes the garbage daemon
    """
    print 'all good to go!'

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


def run_video_job(time_diff):
    print 'video called!!!!!'
    thread_video = Thread(target=take_video)
    thread_timestamp = Thread(target=make_timestamp)

    thread_video.start()
    thread_timestamp.start()
    thread_timestamp.join()

    print CAMERA_DONE_TEXT + ' ('+ make_timestamp + ')'


def init_camera_daemon():
    # runs scheduled capture from starttime to endtime daily
    print camera_start
    job = sched.add_job(run_video_job, 'cron', hour=int(camera_start[0]), minute=int(camera_start[1]), args=[camera_time_diff])
    sched.start()


if __name__ == '__main__':
    prog()

