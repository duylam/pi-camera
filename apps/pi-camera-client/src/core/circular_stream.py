import threading
import time
import os
import io
import picamera

class CircularStream:
    def __init__(self, buffer_size):
        self._buffer_size = buffer_size
        self._circular_io = picamera.CircularIO(buffer_size)
        self._num_bytes_written = 0

    #
    # Implement the file-like reading interface that aiortc.MediaPlayer requires
    # See: https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/container/core.pyx#L171
    #
    @property
    def writable(self):
        return False

    def read(self):
        # Simulate the behavior from
        # https://docs.python.org/3/library/io.html#io.RawIOBase.read
        if self._num_bytes_written == 0:
          return None

        bytes_read = None
        num_bytes_to_read = self._num_bytes_written
        if self._num_bytes_written <= self._buffer_size:
            # The buffer contain entire data written till now
            self._circular_io.seek(0)
        else:
            # The entire data written till now exceeds the buffer size (oldest part
            # has been overrided). So the amount of data to read is entire buffer, but
            # we need to find the position to begin reading
            # See below diagram for buffer state
            # At t0, write 02 bytes: [ _ _ P _ ] The position P is for next writing
            # At t1, write 03 bytes: [ _ P _ _ ] Our beginning of reading position is P 
            num_bytes_to_read = self._buffer_size

            if self._circular_io.tell() == self._buffer_size:
                self._circular_io.seek(0)
            else:
                self._circular_io.seek(1, 1)

        bytes_read = self._circular_io.read1(num_bytes_to_read)

        self._circular_io.seek(0)
        self._num_bytes_written = 0
        return bytes_read

    #
    # END
    #

    # We don't want to expose write() so that aiortc.MediaPlayer thinks this is read-only stream
    def write_(self, byte_s):
        self._num_bytes_written = self._num_bytes_written + self._circular_io.write(byte_s)

    def close():
       self._circular_io.close()

