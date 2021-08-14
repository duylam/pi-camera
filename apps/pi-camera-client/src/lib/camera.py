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
        self._pi_camera_buffer_stream_1 = io.BufferedRandom(
            io.BytesIO(), buffer_size=config.CAMERA_BUFFER_SIZE)
        self._pi_camera_buffer_stream_2 = io.BufferedRandom(
            io.BytesIO(), buffer_size=config.CAMERA_BUFFER_SIZE)
        self._captured_video_frames = set([])
        self._av_codec = None

    async def capture_recording(self) -> None:
        temp_buff = io.BytesIO()
        while not self._pi_frame_queue.empty():
            temp_buff.write(self._pi_frame_queue.get_nowait())
        # Should sleep less 1s, camera can produce data exceeding
        # buffer size on longer sleep time. It produces around
        # 400KB data in 1 second
        #await asyncio.sleep(0.1)

        # Raise error if the PiCamera has any error so that caller can re-init it again
        #self._pi_camera.wait_recording()

        #current_stream = self._pi_camera_buffer_stream_1
        #next_stream = self._pi_camera_buffer_stream_2
        #if current_stream.tell() == 0:
        #    current_stream = self._pi_camera_buffer_stream_2
        #    next_stream = self._pi_camera_buffer_stream_1

        #next_stream.seek(0)
        ## wait for camera to flushing current_stream
        #self._logger.debug("begin")
        #self._pi_camera.split_recording(next_stream)
        #self._logger.debug("after")

        #current_stream.seek(0)
        #captured_video_bytes = current_stream.read()
        #current_stream.seek(0) # indicate the next stream on next loop

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

        await asyncio.sleep(0.01)

    def get_video_video_frames(self) -> set:
        return self._captured_video_frames

    def write(self, buf):
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

            self._pi_camera_buffer_stream_1.close()
            self._pi_camera_buffer_stream_2.close()

            # TODO: how to release self._av_codec
        except:
            pass
