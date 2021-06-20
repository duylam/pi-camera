import logging
import threading
import sys
import io
import os
import picamera
import subprocess
import time
import utils
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

logging.basicConfig(
  format="%(asctime)s [%(levelname)s]: %(message)s",
  level=logging.DEBUG,
  datefmt="%H:%M:%S")

def main():
  KB = 1024
  CAMERA_BUFFER_SIZE = 5*1024*KB
  WEBRTC_VIDEO_TRACK_BUFFER_SIZE = CAMERA_BUFFER_SIZE*4
  VIDEO_RESOLUTION = (1024, 768) # (width, height)
  FRAME_RATE = 20

  circular_stream = utils.CircularStream(buffer_size=WEBRTC_VIDEO_TRACK_BUFFER_SIZE)
  camera = picamera.PiCamera(resolution=VIDEO_RESOLUTION, framerate=FRAMERATE)
  mp4_file = io.open('./final.mp4', mode='wb', buffering=100*KB)
  ffmpeg_process = subprocess.Popen([
    'ffmpeg', '-v', 'quiet', # hide info text
    '-i', '-' # receive .h264 from stdin
    ,'-codec', 'copy', '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1' # write .mp4 to stdout
  ], stdin=subprocess.PIPE, stdout=mp4_file, bufsize=10*1024*KB)

  # See https://picamera.readthedocs.io/en/release-1.13/recipes2.html#splitting-to-from-a-circular-stream
  camera_buffer_stream_1 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)
  camera_buffer_stream_2 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)
  video_track = MediaRelay().subscribe(MediaPlayer(circular_stream))

#VIDEO_RESOLUTION
  #FRAMERATE)

  try:
    count = 1

    pc = RTPeerConnection()

    # quality: For the 'h264' format, use values between 10 and 40 where 10 is extremely
    # high quality, and 40 is extremely low (20-25 is usually a reasonable range for H.264
    # encoding).
    camera.start_recording(camera_buffer_stream_1, format='h264', quality=23)
    while True:
      # Only sleep in 1s, camera can produce data exceeding
      # buffer size on longer sleep time. It produces around
      # 400KB data in 1 second
      camera.wait_recording(1)

      # Read frame info.
      # See https://picamera.readthedocs.io/en/release-1.13/api_camera.html#pivideoframe
      video_frame_info = camera.frame

      current_stream = camera_buffer_stream_1
      next_stream = camera_buffer_stream_2
      if camera_buffer_stream_2.tell() > 0:
        current_stream = camera_buffer_stream_2
        next_stream = camera_buffer_stream_1

      next_stream.seek(0)
      camera.split_recording(next_stream) # wait for camera to flushing current_stream

      current_stream.seek(0)
      video_bytes = current_stream.read()

      logging.debug("Camera produces %d bytes", len(video_bytes))

      if video_bytes: circular_stream.write_(video_bytes)

      if count > 2:
        break
      else:
        count = count + 1
  except:
    logging.exception("Fatal exception")
  finally:
    # Release resources, the order is matter
    if camera.recording: camera.stop_recording()
    camera.close()

    logging.debug("Camera closed")

    if not ffmpeg_process.poll():
      logging.debug("Sending SIGTERM to ffmpeg process")
      ffmpeg_process.terminate()
      logging.debug("Waiting ffmpeg for exiting")
      ffmpeg_process.wait()

    if not mp4_file.closed:
      logging.debug("Closing file")
      mp4_file.close()

    circular_stream.close()

if __name__ == "__main__":
  #  main()
  buffer = picamera.CircularIO(4)
  buffer.write(b"\x0a\x0b\x0c")
  buffer.seek(0)
  content = buffer.read()
  logging.debug(content)

  buffer.write(b"\x0e\x0e\x0f\x0f")
  buffer.seek(-4, 1)
  content = buffer.readall()
  logging.debug(content)

  buffer.write(b"\x0e\x0f")

  content = buffer.readall()
  logging.debug(content)
