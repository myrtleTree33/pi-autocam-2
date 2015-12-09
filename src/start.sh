#!/usr/bin/env sh

###############################################
## Bootloader script to take videos.
###############################################

## Create empty dir for storing recordings, if not available
mkdir -p rec

## Script to run camcorder.
## In the event of failure, press ctrl + \ to dump program.

## Start taking photos
## Modify numbers as required here.
## Do note that screen dimensions must be in 16:9 ratio, else program fails.

python pi-video.py --fps 8 --width 160 --height 90 --start 1212 --end 1213 --bitrate 1000000 --id 001 --filelifespan 2678400
