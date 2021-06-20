import logging, io
import picamera
from core import const

CAMERA_BUFFER_SIZE = 5*1024*const.KB
VIDEO_RESOLUTION = (1024, 768) # (width, height)
FRAME_RATE = 20

class Camera {
    def __init__(self, video_resolution = VIDEO_RESOLUTION, framerate = FRAME_RATE):
      self._pi_camera = picamera.PiCamera(resolution=VIDEO_RESOLUTION, framerate=FRAMERATE)
      self._pi_camera_buffer_stream_1 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)
      self._pi_camera_buffer_stream_2 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)

    def capture_recording(self):

    def get_recording(self):

    def close(self):


}

