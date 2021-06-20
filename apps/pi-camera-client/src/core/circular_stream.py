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
        if self._num_bytes_written <= self._buffer_size:
            # The buffer contain entire data written till now
            self._circular_io.seek(0)
            bytes_read = self._circular_io.read(self._num_bytes_written)
        else:
            # The entire data written till now exceeds the buffer size (oldest part
            # has been overrided). So the amount of data to read is entire buffer
            num_bytes_to_read = self._buffer_size
            num_bytes_to_read_till_buffer_end = self._buffer_size - self._circular_io.tell()
            bytes_read_end = self._circular_io.read(num_bytes_to_read_till_buffer_end)
            self._circular_io.seek(0)
            bytes_read_begin = self._circular_io.read(self._buffer_size - len(bytes_read_end))
            bytes_read = bytes_read_begin + bytes_read_end


            # Find the position to begin reading which is after .tell(), see below
            # At t0, write 02 bytes: [ _ _ P _ ] The position P is for next writing
            # At t1, write 03 bytes: [ _ P _ _ ] Our beginning of reading position is P 
            #if self._circular_io.tell() == 0:
            #    self._circular_io.seek(0, 2)
            #else:
            #    self._circular_io.seek(-1, 1)


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

