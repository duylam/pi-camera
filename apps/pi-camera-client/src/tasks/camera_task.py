import logging, queue

from lib import Camera

async def run(outgoing_video_chunk_queue):
  camera = Camera()
  camera.start()

  # Read frame info.
  # See https://picamera.readthedocs.io/en/release-1.13/api_camera.html#pivideoframe
  #video_frame_info = camera.frame

  while True:
    camera.capture_recording()
    video_bytes = camera.get_video_bytes()
    if video_bytes:
        if outgoing_video_chunk_queue.full():
            logging.warning('The video queue is full, skip the chunk')
            continue

        try:
            outgoing_video_chunk_queue.put_nowait(video_bytes)
        except:
            logging.exception('Error on writing video chunk to queue')

