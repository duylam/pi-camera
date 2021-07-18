import av, os, logging, io, asyncio
from lib import const, config

import inspect

class Camera:
   def __init__(self, video_resolution = config.VIDEO_RESOLUTION, framerate = config.FRAMERATE):
       self._fh = None
       self._captured_video_frames = set([])
       self._av_codec = None

   async def capture_recording(self) -> None:
       await asyncio.sleep(1)

       if not self._fh or self._fh.closed:
           logging.debug('openning file')
           self._fh = open(os.path.join(os.getcwd(), 'video.h264'), 'rb')

       captured_video_bytes = self._fh.read(1<<16)
       logging.debug("read %s bytes", len(captured_video_bytes))

       if not captured_video_bytes:
           logging.debug('closing file')
           self._fh.close()
           return

       packets = self._av_codec.parse(captured_video_bytes)
       self._captured_video_frames = []
       for packet in packets:
           frames = self._av_codec.decode(packet)
           for f in frames:
               self._captured_video_frames.append(f)

   def get_video_video_frames(self):
       return self._captured_video_frames

   def __enter__(self):
       self._av_codec = av.CodecContext.create('h264', 'r')
       return self

   def __exit__(self, exc_type, exc_val, exc_tb):
       try:
           self._fh.close()
       except:
           pass

