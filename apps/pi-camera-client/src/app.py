import logging, asyncio
import sys
import io
import os
import subprocess
import time
from queue import Queue
from camera_task import run as run_camera
from rtc_signaling_task import run as run_rtc_signaling
from main_task import run as run_main

logging.basicConfig(
  format="%(asctime)s [%(levelname)s]: %(message)s",
  level=logging.DEBUG,
  datefmt="%H:%M:%S")

async def main():
  new_video_chunk_queue = Queue(20)
  incoming_rtc_request_queue = Queue(50)
  outgoing_rtc_response_queue = Queue(50)
  WEBRTC_VIDEO_TRACK_BUFFER_SIZE = CAMERA_BUFFER_SIZE*4

  # See https://picamera.readthedocs.io/en/release-1.13/recipes2.html#splitting-to-from-a-circular-stream
  video_track = MediaRelay().subscribe(MediaPlayer(circular_stream))

#VIDEO_RESOLUTION
  #FRAMERATE)

  try:
    await asyncio.gather(
        run_camera(outgoing_video_chunk_queue=new_video_chunk_queue),
        run_rtc_signaling(
            request_queue=incoming_rtc_request_queue,
            response_queue=outgoing_rtc_response_queue
            out_video_chunk_queue=new_video_chunk_queue
        ),
        run_main(
            new_video_chunk_queue=new_video_chunk_queue,
            incoming_rtc_request_queue=incoming_rtc_request_queue,
            outgoing_rtc_response_queue=outgoing_rtc_response_queue
        )
    )
  except KeyboardInterrupt:
    logging.debug('Received exit, exiting')
  except:
    logging.exception('Fatal exception')

if __name__ == "__main__":
  asyncio.run(main())

