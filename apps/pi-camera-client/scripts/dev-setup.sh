#!/bin/bash

VENDOR_DIR="./vendors"
sudo apt-get update

mkdir $VENDOR_DIR || true

# Install h264 library
if [ ! -d "$VENDOR_DIR/x264" ]; then
  echo "* Installing h264 library"
  git clone --depth 1 https://code.videolan.org/videolan/x264 $VENDOR_DIR/x264
  cd $VENDOR_DIR/x264
  ./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
  make -j4
  sudo make install
fi

# Install ffmpeg
if ! command -v ffmpeg -v quiet &> /dev/null; then
  echo "* Installing ffmpeg"
  git clone --depth 1 git://source.ffmpeg.org/ffmpeg $VENDOR_DIR/ffmpeg
  cd $VENDOR_DIR/ffmpeg
  ./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree
  make -j4
  sudo make install
fi

# Python3 required
if ! command -v python3 &> /dev/null; then
  echo "* Installing python3"
  sudo apt install python3
fi

