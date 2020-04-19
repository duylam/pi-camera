#!/bin/bash

cd ~
mkdir ./src || true

# Install h264 library
git clone --depth 1 https://code.videolan.org/videolan/x264 ~/src/x264
cd ~/src/x264
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
make -j4
sudo make install

# Install ffmpeg
git clone --depth=1 git://source.ffmpeg.org/ffmpeg ~/src/ffmpeg
cd ~/src/ffmpeg
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree
make -j4
sudo make install
