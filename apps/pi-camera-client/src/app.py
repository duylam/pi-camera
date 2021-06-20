import logging
import threading
import sys
import io
import os
import subprocess
import time
from camera import Camera
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

logging.basicConfig(
  format="%(asctime)s [%(levelname)s]: %(message)s",
  level=logging.DEBUG,
  datefmt="%H:%M:%S")

def main():
  WEBRTC_VIDEO_TRACK_BUFFER_SIZE = CAMERA_BUFFER_SIZE*4

  camera = Camera()
  mp4_file = io.open('./final.mp4', mode='wb', buffering=100*KB)

  # See https://picamera.readthedocs.io/en/release-1.13/recipes2.html#splitting-to-from-a-circular-stream
  video_track = MediaRelay().subscribe(MediaPlayer(circular_stream))

#VIDEO_RESOLUTION
  #FRAMERATE)

  try:
    count = 1

    camera.start()
    while True:
      camera.capture_recording():

      # Read frame info.
      # See https://picamera.readthedocs.io/en/release-1.13/api_camera.html#pivideoframe
k     video_frame_info = camera.frame

      # Loop list of webrtc to append video bytes
      video_bytes = camera.get_video_bytes()

      logging.debug("Camera produces %d bytes", len(video_bytes))

      if video_bytes: True

      if count > 2:
        break
      else:
        count = count + 1
  except:
    logging.exception("Fatal exception")
  finally:
    # Release resources, the order is matter
    camera.end()
    logging.debug("Camera closed")

    if not mp4_file.closed:
      logging.debug("Closing file")
      mp4_file.close()

if __name__ == "__main__":
  main()

