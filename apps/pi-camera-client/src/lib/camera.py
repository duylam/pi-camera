import logging
import io
import asyncio
import picamera
import av
import queue
from lib import const, config

class Camera:
    def __init__(self, debug_ns: str):
        self._pi_frame_queue = queue.Queue(500)
        self._cam_buffer = io.BytesIO()
        self._logger = logging.getLogger("{}.camera_module".format(debug_ns))
        self._pi_camera = picamera.PiCamera()
        self._pi_camera.framerate = config.FRAMERATE
        self._captured_video_frames = set([])
        self._av_codec = None

    async def capture_recording(self) -> None:
        temp_buff = io.BytesIO()

        if self._pi_frame_queue.empty():
            await asyncio.sleep(0.01)
            return

        while not self._pi_frame_queue.empty():
            temp_buff.write(self._pi_frame_queue.get_nowait())

        # Convert .H264 bytes to set([av.Frame])
        # See https://pyav.org/docs/develop/cookbook/basics.html#parsing
        if temp_buff.tell() > 0:
            temp_buff.truncate()
            temp_buff.seek(0)
            packets = self._av_codec.parse(temp_buff.getvalue())
            self._captured_video_frames = set([])
            for packet in packets:
                frames = self._av_codec.decode(packet)
                self._captured_video_frames = self._captured_video_frames | set(
                    frames)

    def clear_video_video_frames(self) -> None:
        self._captured_video_frames = set([])

    def get_video_video_frames(self) -> set:
        return self._captured_video_frames

    def write(self, buf):
        # Start new H264 frame ?
        if buf.startswith(b'\x00\x00\x00\x01'):
            self._cam_buffer.truncate()
            self._pi_frame_queue.put_nowait(self._cam_buffer.getvalue())
            self._cam_buffer.seek(0)

        return self._cam_buffer.write(buf)

    def __enter__(self):
        # quality: For the 'h264' format, use values between 10 and 40 where 10 is extremely
        # high quality, and 40 is extremely low (20-25 is usually a reasonable range for H.264
        # encoding).
        self._pi_camera.start_recording(
            self, format='h264',
            # See https://www.rgb.com/h264-profiles
            profile='baseline',
            resize= config.VIDEO_RESOLUTION,
            quality=config.VIDEO_QUALITY_OPTION)
        self._av_codec = av.CodecContext.create('h264', 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._pi_camera.recording:
                self._pi_camera.stop_recording()
            self._pi_camera.close()

            # TODO: how to release self._av_codec
        except:
            pass
