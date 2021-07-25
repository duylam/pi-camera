#!/bin/bash

set -e # stop at error

echo "Creating .h264 video"
raspivid -o video.h264 -t 1000 # record in 1 second

echo "Checking format"
ffprobe -show_streams -select_streams v:0 -show_format -v quiet video.h264

