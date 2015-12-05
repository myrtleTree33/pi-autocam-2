# -*- coding: utf-8 -*-

import click
import sys
import time
import os
import subprocess
import datetime
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

## Set maximum lifespan of file before it is deleted
MAX_LIFESPAN_FILE_SECS = 60 * 60 * 24 * 31  ## 31 days

## Sets time to run garbage colllector job
GARBAGE_CHECK_TIME_SECS = 10  ## 10 seconds

def make_command(command, val):
    return "--" + command + " " + str(val)

def take_video(duration):
    startRec = "./hooks/start_record"
    stopRec = "./hooks/stop_record"

    # remove all files
    try:
        os.remove(startRec)
        os.remove(stopRec)
    except Exception:
        pass

    print 'Starting video capture..'
    subprocess.call(["touch", startRec])
    time.sleep(duration)
    subprocess.call(["touch", stopRec])
    time.sleep(2)
    print 'Ending video capture..'


def calc_time_diff(startTuple, endTuple):
    """
    Retrieves the number of seconds between 2 time tuples
    """
    print startTuple, endTuple
    start = datetime.datetime(year=2014, month=2, day=14, hour=startTuple[0], minute=startTuple[1])
    end = datetime.datetime(year=2014, month=2, day=14, hour=endTuple[0], minute=endTuple[1])
    secs = (end - start).total_seconds()
    print('Running for %d secs..' % (secs))
    return secs



@click.command()
@click.option('--fps', default=2, help='Frames per second/')
@click.option('--width', default=160, help='The screen capture width')
@click.option('--height', default=90, help='The screen capture height')
@click.option('--videobitrate', default=500000, help='The video bit rate of each file')
@click.option('--start', default='0700', help='Video start time')
@click.option('--end', default='1800', help='Video end time')
def prog(fps, width, height, videobitrate, start, end):
    """
    Simple program to take pictures
    """

    ## Catch various errors
    if (fps < 2):
        raise ValueError('FPS is too low.  Please choose a higher FPS.')
        sys.exit(-1)
    if (float(16) / 9) != (float(width) / height):
        raise ValueError('Aspect ratio not in 16:9.  Please set accordingly.')
        sys.exit(-1)

    # Start and end times as a tuple
    startTuple = (int(start[:2]), int(start[2:]))
    endTuple = (int(end[:2]), int(end[2:]))

    args = " " + make_command("fps", fps) + " " + make_command("width", width) + " " + make_command("height", height) + " " + make_command("videobitrate", videobitrate)

    ## Run the daemons ----------
    init_garbage_daemon('./rec', MAX_LIFESPAN_FILE_SECS, GARBAGE_CHECK_TIME_SECS)
    run_cam_daemon(args)
    ## --------------------------

    # runs scheduled capture from starttime to endtime daily
    sched = BlockingScheduler()
    timeDiff = calc_time_diff(startTuple, endTuple)
    if (timeDiff < 0):
        raise ValueError('EndTime is earlier than StartTime.  Please correct!')
        sys.exit(-1)
    job = sched.add_job(take_video, 'cron', hour=int(startTuple[0]), minute=int(startTuple[1]), args=[timeDiff])
    sched.start()


def run_cam_daemon(args):
    print args
    print 'cam daemon running..'
    ## UNCOMMENT BEFORE FLIGHT
    subprocess.Popen(['./picam'] + args.split(' '))
    time.sleep(1)

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

    thread = Thread(target = garbage_daemon, args = (folder, lifespan_secs, interval_secs))
    thread.start()


if __name__ == '__main__':
    print "Running timer.."
    prog()
