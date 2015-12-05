#!/usr/bin/env sh

###############################################
## Bootloader script to take videos.
###############################################

## Script to run camcorder.
## In the event of failure, press ctrl + \ to dump program.

## Start taking photos
## Modify numbers as required here.
## Do note that screen dimensions must be in 16:9 ratio, else program fails.
## Please check Picam manual for more information.
## Features: Picam apparently uses Hardware embedded MPEG encoder for TS files
## So this offsets load from Raspberry Pi to the hardware itself.
#python main.py --fps 2 --width 160 --height 90 --start 0030 --end 2100 --videobitrate 500000
python pi-video.py --fps 2 --width 160 --height 90 --start 0030 --end 2100 --videobitrate 1000000 --id 000 --filelifespan 864000
