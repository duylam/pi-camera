import av, os, logging, io, asyncio
from lib import const, config

class Camera:
    def __init__(self, video_resolution = config.VIDEO_RESOLUTION, framerate = config.FRAMERATE):
        self._fh = None
        self._captured_video_frames = set([])
        self._av_codec = None

    async def capture_recording(self) -> None:
        await asyncio.sleep(0.1)

        if not self._fh or not self._fh.readable():
            if self._fh:
                self._fh.close()

            self._fh = open(os.path.join(os.getcwd(), 'video.h264'), 'rb')

        captured_video_bytes = self._fh.read(1<<16)
        packets = self._av_codec.parse(captured_video_bytes)
        self._captured_video_frames = set([])
        for packet in packets:
            frames = self._av_codec.decode(packet)
            self._captured_video_frames = self._captured_video_frames | set(frames)

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

