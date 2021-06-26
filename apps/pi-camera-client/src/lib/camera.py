import logging, io
#import picamera
from core import const

CAMERA_BUFFER_SIZE = 5*1024*const.KB
VIDEO_RESOLUTION = (1024, 768) # (width, height)
FRAME_RATE = 20

class Camera:
    def __init__(self, video_resolution = VIDEO_RESOLUTION, framerate = FRAME_RATE):
        self._pi_camera = None #picamera.PiCamera(resolution=VIDEO_RESOLUTION, framerate=FRAMERATE)
        self._pi_camera_buffer_stream_1 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)
        self._pi_camera_buffer_stream_2 = io.BufferedRandom(io.BytesIO(), buffer_size=CAMERA_BUFFER_SIZE)
        self._captured_video_bytes = None

    def start(self):
        # quality: For the 'h264' format, use values between 10 and 40 where 10 is extremely
        # high quality, and 40 is extremely low (20-25 is usually a reasonable range for H.264
        # encoding).
        camera.start_recording(self._pi_camera_buffer_stream_1, format='h264', quality=23)

    @property
    def buffer_size(self):
        return CAMERA_BUFFER_SIZE

    def capture_recording(self):
        # Only sleep in 1s, camera can produce data exceeding
        # buffer size on longer sleep time. It produces around
        # 400KB data in 1 second
        self._pi_camera.wait_recording(1)

        current_stream = self._pi_camera_buffer_stream_1
        next_stream = self._pi_camera_buffer_stream_2
        if self._pi_camera_buffer_stream_2.tell() > 0:
          current_stream = self._pi_camera_buffer_stream_2
          next_stream = self._pi_camera_buffer_stream_1

        next_stream.seek(0)
        self._pi_camera.split_recording(next_stream) # wait for camera to flushing current_stream

        current_stream.seek(0)
        self._captured_video_bytes = current_stream.read()

    def get_video_bytes(self):
        return self._captured_video_bytes

    def end(self):
        if self._pi_camera.recording: self._pi_camera.stop_recording()
        self._pi_camera.close()

