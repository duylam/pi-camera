import json
import logging
import time
import fractions
import queue
import asyncio

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.mediastreams import MediaStreamError
from aiortc.sdp import candidate_from_sdp
from av.frame import Frame

from lib import config


class RtcConnection:
    def __init__(self, client_id: str, debug_ns: str):
        ns = "{}.rtc_{}".format(debug_ns, client_id)
        self._logger = logging.getLogger(ns)
        self._camera_stream_track = CameraStreamTrack(debug_ns=ns)
        self._answer_confirmed = False

        # See https://aiortc.readthedocs.io/en/stable/api.html#webrtc
        self._pc = RTCPeerConnection(RTCConfiguration([RTCIceServer(config.ICE_SERVER_URLS)]))
        self._client_id = client_id

        @self._pc.on("connectionstatechange")
        def on_connectionstatechange():
            self._logger.debug("[Event: connectionstatechange] Connection state is %s" % self._pc.connectionState)

    @property
    def closed(self) -> bool:
        return self._pc.connectionState == 'closed' or self._pc.connectionState == 'failed'

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def ready(self) -> bool:
        return self._answer_confirmed and self._pc.signalingState == 'stable'

    def append_video_frames(self, video_frames: set) -> None:
        self._camera_stream_track.add_video_frames(video_frames)

    async def add_ice_candidate(self, sdp: str) -> None:
        # Follow code from https://github.com/aiortc/aiortc/blob/a270cd887fba4ce9ccb680d267d7d0a897de3d75/src/aiortc/contrib/signaling.py#L22
        json_msg = json.loads(sdp)
        candidate = candidate_from_sdp(sdp)
        candidate.sdpMid = json_msg["sdpMid"]
        candidate.sdpMLineIndex = json_msg["sdpMLineIndex"]
        await self._pc.addIceCandidate(candidate)

    async def create_offer(self) -> str:
        self._logger.debug('Adding track to peer connection')
        self._pc.addTrack(self._camera_stream_track)

        self._logger.debug('Creating SDP offer')
        session_description = await self._pc.createOffer()

        self._logger.debug('Calling setLocalDescription()')
        await self._pc.setLocalDescription(session_description)
        return self._pc.localDescription.sdp

    async def receive_answer(self, answer_sdp) -> None:
        self._logger.debug('Calling setRemoteDescription()')
        await self._pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type='answer'))

    def confirm_answer(self) -> None:
        self._answer_confirmed = True

    async def close(self) -> None:
        self._logger.debug('Closing peer connection')
        await self._pc.close()


"""
Customize code from VideoStreamTrack
at https://github.com/aiortc/aiortc/blob/d5d1d1f66c4c583a3d8ebf34f02d76bc77a6d137/src/aiortc/mediastreams.py#L109
"""
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1/config.FRAMERATE
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
VIDEO_PRESENTATION_TIMESTAMP_CLOCK = int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
WAIT_FOR_NEW_FRAME_SECOND = (1/config.FRAMERATE)/1000

class CameraStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, debug_ns: str, frames_queue_size=50):
        super().__init__()

        self._logger = logging.getLogger("{}.media_track".format(debug_ns))
        self._frames_queue = queue.Queue(maxsize=frames_queue_size)
        self._timestamp: int = 0

    """
    Receives list of av.Frame representing for video from Camera module
    """
    def add_video_frames(self, frames: []) -> None:
        if self.readyState != 'live':
            return

        for f in frames:
            # Error on adding one frame is ignored since we're streaming from camera
            try:
                if self._frames_queue.full():
                    # The peer connection sends video frames slower than the camera, then we just ignore the oldest frame
                    self._frames_queue.get_nowait()

                # The RTCRtpSender in aiortc requires the attribute .time_base and .pts on sending the video frame. However, the generated
                # av.Frame doesn't have them. So we make these fields accordingly with the timestamp that this CameraStreamTrack receives
                # See explanation for them at https://stackoverflow.com/a/43337235
                #
                # See their definition at https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/frame.pyx#L113
                f.time_base = VIDEO_TIME_BASE
                f.pts = self._timestamp
                self._frames_queue.put_nowait(f)
            except:
                self._logger.warning(
                    'Failed to add video frame from Camera to sending queue, skip this video frame')
            finally:
                self._timestamp += VIDEO_PRESENTATION_TIMESTAMP_CLOCK

    #
    # Below methods are implementation for base class MediaStreamTrack
    #
    async def recv(self) -> Frame:
        frame = None
        while True:
            # Make sure frames are available to send to other peer
            while self._frames_queue.empty():
                await asyncio.sleep(WAIT_FOR_NEW_FRAME_SECOND)

            try:
                frame = self._frames_queue.get()
                break
            except:
                pass

        return frame

