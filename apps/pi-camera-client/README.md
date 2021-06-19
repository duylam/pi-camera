A Python app captures H264 video from Camera module, wrap with MP4 container and sends to TURN server in WebRTC protocol

**Table of Content**

<!--TOC-->

- [Table of Contents](#table-of-contents)
- [1. Prerequisite](#1-prerequisite)
- [2. Development setup](#2-development-setup)
- [3. Coding workflow](#3-coding-workflow)
- [4. Other commands](#4-other-commands)
- [4. Other Proof of Concept app](#4-other-proof-of-concept-app)
  - [4.1 Record camera](#41-record-camera)
  - [4.2 Wrap mp4 containter](#42-wrap-mp4-containter)
  - [4.3 Check video format](#43-check-video-format)

<!--TOC-->

# 1. Prerequisite

1. Raspberry Pi (tested on Pi 3 Model B)
1. Raspberry Pi OS 8 Jessie (tested)
1. [Camera module installed](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera)

# 2. Development setup 

1. Run `bash scripts/dev-setup.sh` which installs Python3 and other system dependencies
1. (Optional) Use [venv](https://docs.python.org/3/library/venv.html) to create virtual environment. Quick steps as below

  - Create directory for the virtual environment (ignored by git):  `$ python3 -m venv --copies --clear ./.penv`
  - To enter the environment: `$ source ./.penv/bin/activate`
  - To exit the environment: `$ deactivate`

# 3. Coding workflow

1. To install Python libraries: `pip3 install -r requirements.txt`
1. To start app: `python3 src/app.py`

# 4. Other commands

1. To update TOC in README, run `md_toc -p github README.md`
1. To install new Python libraries: `pip3 install --user <name>`. To add to `requirements.txt`
  - Get the version of new installed package: `pip3 show <name>`
  - And then manually update `requirements.txt` 

# 4. Other Proof of Concept app

*Make sure the Camera hardware and software is installed*

## 4.1 Record camera

Run `python poc/camera.py`

## 4.2 Wrap mp4 containter

Run `bash poc/wrap-mp4-container/run.sh`

## 4.3 Check video format

Run `bash poc/check-video-format/run.sh`

