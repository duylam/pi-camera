from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

from lib import CircularStream

# See the doc at https://aiortc.readthedocs.io/en/stable
class RtcConnection:
  def __init__(self, resolution, framerate, buffer_size):
    self._circular_stream = CircularStream(buffer_size=buffer_size)
    self._closed = False

  @property
  def closed(self):
    return self._closed

  def send_video_bytes(self, video_bytes):

  def create_offer(self):



  def receive_answer(self, answer):

  def close(self):
    self._closed = True
