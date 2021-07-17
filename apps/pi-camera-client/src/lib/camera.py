import logging, io, asyncio
import picamera, av
from lib import const, config

class Camera:
    def __init__(self, video_resolution = config.VIDEO_RESOLUTION, framerate = config.FRAMERATE):
        self._pi_camera = picamera.PiCamera(resolution=video_resolution, framerate=framerate)
        self._pi_camera_buffer_stream_1 = io.BufferedRandom(io.BytesIO(), buffer_size=config.CAMERA_BUFFER_SIZE)
        self._pi_camera_buffer_stream_2 = io.BufferedRandom(io.BytesIO(), buffer_size=config.CAMERA_BUFFER_SIZE)
        self._captured_video_frames = set([])
        self._av_codec = None

    @property
    def buffer_size(self) -> int:
        return CAMERA_BUFFER_SIZE

    async def capture_recording(self) -> None:
        # Only sleep in 1s, camera can produce data exceeding
        # buffer size on longer sleep time. It produces around
        # 400KB data in 1 second
        await asyncio.sleep(1)

        # Raise error if the PiCamera has any error so that caller can re-init it again
        self._pi_camera.wait_recording(0)

        current_stream = self._pi_camera_buffer_stream_1
        next_stream = self._pi_camera_buffer_stream_2
        if self._pi_camera_buffer_stream_2.tell() > 0:
          current_stream = self._pi_camera_buffer_stream_2
          next_stream = self._pi_camera_buffer_stream_1

        next_stream.seek(0)
        self._pi_camera.split_recording(next_stream) # wait for camera to flushing current_stream

        current_stream.seek(0)
        captured_video_bytes = current_stream.read()

        # Convert .H264 bytes to set([av.Frame])
        # See https://pyav.org/docs/develop/cookbook/basics.html#parsing
        packets = self._av_codec.parse(captured_video_bytes)
        self._captured_video_frames = set([])
        for packet in packets:
            frames = self._av_codec.decode(packet)
            self._captured_video_frames = self._captured_video_frames | set(frames)

    def get_video_video_frames(self):
        return self._captured_video_frames

    def __enter__(self):
        # quality: For the 'h264' format, use values between 10 and 40 where 10 is extremely
        # high quality, and 40 is extremely low (20-25 is usually a reasonable range for H.264
        # encoding).
        self._pi_camera.start_recording(self._pi_camera_buffer_stream_1, format='h264', quality=23)
        self._av_codec = av.CodecContext.create('h264', 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._pi_camera.recording: self._pi_camera.stop_recording()
            self._pi_camera.close()
        except:
            pass

