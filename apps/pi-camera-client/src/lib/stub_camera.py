import av
import os
import logging
import io
import asyncio
from lib import const, config

video_width, video_height = config.VIDEO_RESOLUTION

# A stub camera for developing without using real Pi box. This
# stub camera produces green frame
class Camera:
    def __init__(self, debug_ns: str):
        self._logger = logging.getLogger("{}.stub_camera".format(debug_ns))
        self._captured_video_frames = set([])

    async def capture_recording(self) -> None:
        await asyncio.sleep(0.1)

        self._captured_video_frames = []

        # Copy from https://github.com/aiortc/aiortc/blob/d5d1d1f66c4c583a3d8ebf34f02d76bc77a6d137/src/aiortc/mediastreams.py#L132
        for x in range(10):
            frame = av.VideoFrame(width=video_width, height=video_height)
            for p in frame.planes:
                p.update(bytes(p.buffer_size))

            self._captured_video_frames.append(frame)

    def clear_video_video_frames(self) -> None:
        self._captured_video_frames = set([])

    def get_video_video_frames(self):
        return self._captured_video_frames

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

