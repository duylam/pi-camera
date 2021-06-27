from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

from lib import CircularStream, config

# See the doc at https://aiortc.readthedocs.io/en/stable
class RtcConnection:
  def __init__(self, buffer_size, client_id, resolution=config.VIDEO_RESOLUTION, framerate=config.FRAMERATE):
    self._circular_stream = CircularStream(buffer_size=buffer_size)
    self._video_resolution = resolution
    self._framerate = framerate
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

  def send_video_bytes(self, video_bytes):
    True

  async def create_offer(self):
    vwidth, vheight = self._video_resolution
    options = {
      "framerate": self._framerate,
      "video_size": "{0}x{1}".format(vwidth, vheight)
    }
    camera = MediaPlayer(self._circular_stream, options=options)
    self._pc.addTrack(MediaRelay().subscribe(camera.video))
    sdp = await self._pc.createOffer()
    await self._pc.setLocalDescripion(sdp)
    return self._pc.localDescription

  async def receive_answer(self, answer):
      await self._pc.setRemoteDescription(answer)

  def confirm_answer(self):
    self._answer_confirmed = True

  def close(self):
    self._pc.close()

