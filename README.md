PiCam
===============================

## What is

Snap videos with the Pi every few seconds.


## Uses

- Wraps the Picam library in C.
- Able to set screen dimensions, frame rate.
- Removes files older than 10 days (untested)



## Installation

- Clone this repository.
- Install `pip`.

        $ sudo apt-get install python-pip

- Install `click` with `pip`

    $ pip install click


## Running the camera

- `cd` into the `src/` directory and run `start.sh`

        $ cd src && ./start.sh

- All videos are found in `rec/`
- To turn the Pi into a server to download video files, use `SimpleHTTPServer`:

        $ cd rec/ && python -m SimpleHTTPServer 3000


## Tweaking / Configuration

- Edit `start.sh` values.
