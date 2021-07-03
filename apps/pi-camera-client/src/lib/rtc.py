import queue, asyncio

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCSessionDescription
from aiortc.mediastreams import MediaStreamError

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
  def ready(self):
    return self._answer_confirmed and self._pc.signalingState == 'stable'

  def append_video_frames(self, video_frames: set):
    self._camera_stream_track.add_video_frames(video_frames)

  async def create_offer(self):
    # https://pyav.org/docs/develop/cookbook/basics.html#parsing
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

class CameraStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, frames_queue_size = 50):
        super().__init__()
        self._frames_queue = queue.Queue(maxsize=frames_queue_size)

    def add_video_frame(frames: set):
        for f in frames:
            # Any error on adding one frame is ignored since we're streaming from camera
            try:
                if self._frames_queue.full():
                    # If the peer connection takes video frames slower than the producing from camera
                    # then we just ignore the oldest frame
                    self._frames_queue.get(timeout=0.1)

                self._frames_queue.put(f, timeout=0.1)
            except:
                pass


    #
    # Below methods are implementation for base class MediaStreamTrack
    # 

    async def recv(self):
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
                # Continue to read next frame if any error
                pass

        return frame


    def stop(self):
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

