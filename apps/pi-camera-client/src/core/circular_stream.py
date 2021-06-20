import threading
import time
import os
import io
import picamera

class CircularStream:
    def __init__(self, buffer_size):
        self._circular_io = picamera.CircularIO(buffer_size)
        self._circular_io.seek(0)
        self._num_bytes_written = 0

    #
    # Implement the file-like reading interface that aiortc.MediaPlayer requires
    # See: https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/container/core.pyx#L171
    #
    @property
    def writable(self):
        return False

    def read(self, n=-1):
        # Simulate the behavior from
        # https://docs.python.org/3/library/io.html#io.RawIOBase.read
        if self._num_bytes_written == 0:
          return None
        self._circular_io.seek(-1 * self._num_bytes_written, 1)
        self._num_bytes_written = 0
        return self._circular_io.read1(n)

    #
    # END
    #

    # We don't want to expose write() so that aiortc.MediaPlayer thinks this is read-only stream
    def write_(self, byte_s):
        self._num_bytes_written = self._num_bytes_written + self._circular_io.write(byte_s)

    def close():
       self._circular_io.close()

