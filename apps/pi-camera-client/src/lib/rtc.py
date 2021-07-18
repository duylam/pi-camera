import queue, asyncio

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCSessionDescription
from aiortc.mediastreams import MediaStreamError
#from aiortc.contrib.signaling import object_from_string
from aiortc.sdp import candidate_from_sdp
from av.frame import Frame
import json, logging, time, fractions

from lib import config

# See the doc at https://aiortc.readthedocs.io/en/stable
class RtcConnection:
  def __init__(self, client_id):
    self._camera_stream_track = CameraStreamTrack()
    self._answer_confirmed = False

    # See https://aiortc.readthedocs.io/en/stable/api.html#webrtc
    self._pc = RTCPeerConnection()
    self._client_id = client_id

  @property
  def closed(self):
    return self._pc.connectionState == 'closed' or self._pc.connectionState == 'failed'

  @property
  def client_id(self):
    return self._client_id

  @property
  def ready(self) -> bool:
    return self._answer_confirmed and self._pc.signalingState == 'stable'

  def append_video_frames(self, video_frames: set) -> None:
    self._camera_stream_track.add_video_frames(video_frames)

  async def add_ice_candidate(self, sdp: str) -> None:
    # Copy from https://github.com/aiortc/aiortc/blob/a270cd887fba4ce9ccb680d267d7d0a897de3d75/src/aiortc/contrib/signaling.py#L22
    json_msg = json.loads(sdp)
    candidate = candidate_from_sdp(sdp)
    candidate.sdpMid = json_msg["sdpMid"]
    candidate.sdpMLineIndex = json_msg["sdpMLineIndex"]
    await self._pc.addIceCandidate(candidate)

  async def create_offer(self):
    # https://github.com/jlaine/aiortc/blob/6edad395544348702e124d8e3f31a44a2a04654c/src/aiortc/contrib/media.py#L154
    self._pc.addTrack(self._camera_stream_track)
    session_description = await self._pc.createOffer()
    await self._pc.setLocalDescription(session_description)
    return self._pc.localDescription.sdp

  async def receive_answer(self, answer_sdp):
    await self._pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type='answer'))

  def confirm_answer(self):
    self._answer_confirmed = True

  def close(self):
    self._pc.close()

"""
Follow implementation of VideoStreamTrack
at https://github.com/aiortc/aiortc/blob/d5d1d1f66c4c583a3d8ebf34f02d76bc77a6d137/src/aiortc/mediastreams.py#L109
"""
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 20  # 20fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
VIDEO_TIMESTAMP_DURATION = int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
class CameraStreamTrack(MediaStreamTrack):
   kind = "video"

   def __init__(self, frames_queue_size = 50):
       super().__init__()
       self._start = None
       self._frames_queue = queue.Queue(maxsize=frames_queue_size)
       self._start = None
       self._timestamp = None

   def add_video_frames(self, frames: set):
       #logging.debug("queue length before in add_video_frames %s", self._frames_queue.qsize())
       for f in frames:
           # Any error on adding one frame is ignored since we're streaming from camera
           try:
               if self._frames_queue.full():
                   # If the peer connection takes video frames slower than the producing from camera
                   # then we just ignore the oldest frame
                   self._frames_queue.get(timeout=0.1)

               self._frames_queue.put(f, timeout=0.1)
           except:
               logging.exception('adding frame to queue error, try to add next')
               pass
       
       #logging.debug("queue length after in add_video_frames %s", self._frames_queue.qsize())

   async def _next_timestamp(self) -> int:
       if self._timestamp:
           self._timestamp += VIDEO_TIMESTAMP_DURATION
           wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
           await asyncio.sleep(wait)
       else:
           self._start = time.time()
           self._timestamp = 0

       return self._timestamp

   #
   # Below methods are implementation for base class MediaStreamTrack
   # 
   async def recv(self) -> Frame:
       if self.readyState != 'live':
           raise MediaStreamError

       frame = None
       while True:
           while self._frames_queue.empty():
               await asyncio.sleep(0.05)

           try:
               frame = self._frames_queue.get_nowait()
               break
           except:
               logging.exception('getting frame from queue error, trying to get next frame')
               # Continue to read next frame if any error
               #pass

       pts = await self._next_timestamp()

       # See https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/frame.pyx#L80
       frame.pts = pts

       # See https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/frame.pyx#L113
       frame.time_base = VIDEO_TIME_BASE

       return frame

   def stop(self) -> None:
       super().stop()

       error_count = 0
       while not self._frames_queue.empty():
           try:
               if error_count >= 3:
                   # We might have leaked memory in queue contains items, but we can't
                   # let the loop run infinitely
                   break
               self._frames_queue.get(block=False)
           except:
               error_count = error_count + 1
               pass

