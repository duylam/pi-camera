#!/bin/bash

set -e # stop at error

echo "Creating .h264 video"
raspivid -o video.h264 -t 5000 # record in 5 seconds

echo "Wrap mp4 container on .h264 video"
ffmpeg -i video.h264 -codec copy -movflags frag_keyframe+empty_moov -f mp4 video.mp4

echo "See video.mp4 file"

