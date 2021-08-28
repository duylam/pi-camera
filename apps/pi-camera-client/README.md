A Python app captures H264 video from Camera module, wrap with MP4 container and sends to TURN server in WebRTC protocol

**Table of Content**

<!--TOC-->

- [1. Prerequisite](#1-prerequisite)
- [2. Development setup](#2-development-setup)
- [3. Coding workflow](#3-coding-workflow)
- [4. Other commands](#4-other-commands)
- [4. Other Proof of Concept app](#4-other-proof-of-concept-app)
  - [4.1 Record camera](#41-record-camera)
  - [4.2 Wrap mp4 containter](#42-wrap-mp4-containter)
  - [4.3 Check video format](#43-check-video-format)
- [5. Technical notes](#5-technical-notes)
- [6. Camera module troubleshooting](#6-camera-module-troubleshooting)
  - [6.1 Error "mmal: mmal_vc_component_create: failed to create component 'vc.ril.camera'"](#61-error-mmal-mmal_vc_component_create-failed-to-create-component-vcrilcamera)
  - [6.2 Error "mmal: No data received from sensor. Check all connections, including the Sunny one on the camera board"](#62-error-mmal-no-data-received-from-sensor-check-all-connections-including-the-sunny-one-on-the-camera-board)

<!--TOC-->

# 1. Prerequisite

1. Raspberry Pi (tested on Pi 3 Model B)
1. Raspberry Pi OS 8 Jessie (tested)
1. [Camera module installed](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera)
  - The Camera can be damaged easily due to [Electrostatic discharge](https://en.wikipedia.org/wiki/Electrostatic_discharge) (see more [here](https://raspberrypi.stackexchange.com/questions/12265/how-to-protect-rpi-camera-from-esd)). So make sure **DO NOT** touch it while the it connects to Pi and the Pi's power is on.
  - To verify the Camera works: `raspistill -o /tmp/image.jpg`

# 2. Development setup 

1. Run `bash scripts/dev-setup.sh` which installs Pythoni 3.5+ and other system dependencies
1. See necessary environment at `src/lib/config.py`. You can create `.env` file for predefine env var for local development, see [python-dotenv](https://pypi.org/project/python-dotenv/)

# 3. Coding workflow

Run `source scripts/dev-shell.sh` setup and go into virtual environment

> Below commands are supposed to run inside the virtual env

**To launch on Pi box**

Launch the app: `python3 src/app.py`

**To launch on non Pi box (macOS, Ubuntu machine)**

- Edit `src/lib/__init__.py` to change the Camera class to use `stub_camera` module 
- Launch the app: `python3 src/app.py`

# 4. Other commands

> Below commands are supposed to run inside the virtual env

1. To update TOC in README, run `md_toc -p github README.md`
1. To run unit test: `bash scripts/test.sh`
1. To run specific test method: `python3 -m unittest test.core.test_circular_stream.TestCircularStream.test_read_over_num_when_availale`
1. To add new lib as production dependeny: `poetry add <name>`. For adding as development one: `poetry add --dev <name>`
1. Format code: `autopep8  src/ test/`. And the commit changed files
1. Create build package: `poetry build --format sdist`

# 4. Other Proof of Concept app

*Make sure the Camera hardware and software is installed*

## 4.1 Record camera

Run `python poc/camera.py`

## 4.2 Wrap mp4 containter

Run `bash poc/wrap-mp4-container/run.sh`

## 4.3 Check video format

Run `bash poc/check-video-format/run.sh`

# 5. Technical notes

- [Python generated from .proto](https://developers.google.com/protocol-buffers/docs/reference/python-generated)
- [Python grpc example with asyncio module](https://github.com/grpc/grpc/blob/master/examples/python/route_guide/asyncio_route_guide_client.py)
- [Sample .h264 video files](https://www.fastvdo.com/H.264.html)
- [WebRTC signaling workflow](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling)

# 6. Camera module troubleshooting

## 6.1 Error "mmal: mmal_vc_component_create: failed to create component 'vc.ril.camera'"

- Make sure Camera module is installed correctly, see [guideline](https://www.youtube.com/watch?v=GImeVqHQzsE)
- Check GPU has seen the sensor or not: `vcgencmd get_camera`. On the result, `0` means "can't see"
- Check Pi can see Camera or not: `raspistill -v `

## 6.2 Error "mmal: No data received from sensor. Check all connections, including the Sunny one on the camera board"

Sadly, it's properly the Camera was damaged due to electrostatic discharge. See note at top. The only option is to buy new one :(

