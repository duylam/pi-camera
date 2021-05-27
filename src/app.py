import logging
import threading
import sys
import io
import os
import picamera
import subprocess
import time
import utils

logging.basicConfig(
  format="%(asctime)s [%(levelname)s]: %(message)s",
  level=logging.DEBUG,
  datefmt="%H:%M:%S")

def main():
  KB = 1024
  camera = picamera.PiCamera()
  mp4_file = io.open('./final.mp4', mode='wb', buffering=100*KB)
  ffmpeg_process = subprocess.Popen([
    'ffmpeg', '-v', 'quiet', # hide info text
    '-i', '-' # receive .h264 from stdin
    ,'-codec', 'copy', '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1' # write .mp4 to stdout
  ], stdin=subprocess.PIPE, stdout=mp4_file, bufsize=10*1024*KB)

  buffer_stream_1 = io.BufferedRandom(io.BytesIO(), buffer_size=5*1024*KB)
  buffer_stream_2 = io.BufferedRandom(io.BytesIO(), buffer_size=5*1024*KB)

  try:
    count = 1

    # Set the quantization parameter which will cause the video encoder to use VBR (variable bit-rate) encoding.
    # This can be considerably more efficient especially in mostly static scenes (which can be important when recording to memory)
    camera.start_recording(buffer_stream_1, format='h264', quantization=23)
    while True:
      # Only sleep in 1s, camera can produce data exceeding
      # buffer size on longer sleep time. It produces around
      # 400KB data in 1 second
      camera.wait_recording(1)

      current_stream = buffer_stream_1
      next_stream = buffer_stream_2
      if buffer_stream_2.tell() > 0:
        current_stream = buffer_stream_2
        next_stream = buffer_stream_1

      next_stream.seek(0)
      camera.split_recording(next_stream) # wait for camera to flushing current_stream

      current_stream.seek(0)
      video_bytes = current_stream.read()

      logging.debug("Camera produces %d bytes", len(video_bytes))

      if video_bytes: ffmpeg_process.stdin.write(video_bytes)

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

if __name__ == "__main__":
  main()

