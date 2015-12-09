PiCam
===============================

## What is

Deploys Raspberry Pi and camera as a security camera unit.


## Features

- Records in H264 format
- Ability to remove older videos exceeding specified lifetime
- Able to display live video feed, while recording H264 video files
- Able to view live video feed at http://localhost:5000
- Able to timestamp and show camera ID stamps on video


## Installation

- Clone this repository.
- Install `pip`.

        $ sudo apt-get install python-pip

- Install dependencies

        $ pip install click
        $ pip install apscheduler
        $ pip install picamera
        $ pip install flask


## Running the camera

- `cd` into the `src/` directory and run `start.sh`

        $ cd src && ./start.sh

- All videos are found in `rec/`


## Live video feed

- Live video feed available at http://localhost:5000


## Tweaking / Configuration

- To view available parameters, tweak `start.sh` and view the help sequence

      $ python pi-video.py --help
