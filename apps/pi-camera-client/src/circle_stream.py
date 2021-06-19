import threading
import time
import os
import io

class CircularStream {
    def __init__(self, circular_io):
      self.circular_io = circular_io
      self.num_bytes_written = 0

    #
    # Implement the interface that aiortc.MediaPlayer requires
    # See: https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/container/core.pyx#L171
    #
    @property
    def writable(self):
      return False

    def read(n=-1):
      # Simulate the behavior from
      # https://docs.python.org/3/library/io.html#io.RawIOBase.read
      if self.num_bytes_written == 0:
        return None
      self.circular_io.seek(-1 * self.num_bytes_written, 1)
      self.circular_io.read1(n)
      self.num_bytes_written = 0

    #
    # END
    #

    def write_(self, byte_s):
      self.num_bytes_written = self.num_bytes_written + self.cicular_io.write(byte_s)
}

