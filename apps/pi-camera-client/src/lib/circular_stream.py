import threading
import time
import os
import io
import picamera

class CircularStream:
    def __init__(self, buffer_size):
        self._buffer_size = buffer_size
        self._last_position = buffer_size - 1
        self._circular_io = picamera.CircularIO(buffer_size)
        self._read_position = 0
        self._num_bytes_written = 0

    #
    # Implement the file-like reading interface that aiortc.MediaPlayer requires
    # See: https://github.com/PyAV-Org/PyAV/blob/9ac05d9ac902d71ecb2fe80f04dcae454008378c/av/container/core.pyx#L171
    #
    @property
    def writable(self):
        return False

    def read(self, n=-1):
        # Fulfill the behavior from
        # https://docs.python.org/3/library/io.html#io.RawIOBase.read
        if self._num_bytes_written == 0:
          return b''

        bytes_read = None
        bytes_to_read = None
        write_position = self._circular_io.tell()

        if n > 0:
            bytes_to_read = min(n, self._num_bytes_written)
        else:
            bytes_to_read = self._num_bytes_written

        position_after_read = self._read_position + bytes_to_read - 1
        is_within_buffer = position_after_read <= self._last_position

        self._circular_io.seek(self._read_position, 0)
        if is_within_buffer:
            bytes_read = self._circular_io.read(bytes_to_read)
        else:
            # Need to read twice: till end of buffer AND beginning of buffer
            bytes_read_begin = self._circular_io.read()
            self._circular_io.seek(0)
            bytes_read_end = self._circular_io.read(bytes_to_read - len(bytes_read_begin))
            bytes_read = bytes_read_begin + bytes_read_end

        self._read_position = self._circular_io.tell()
        self._num_bytes_written -= bytes_to_read
        self._circular_io.seek(write_position, 0)

        return bytes_read

    #
    # END
    #

    # We don't want to expose write() so that aiortc.MediaPlayer thinks this is read-only stream
    def write_(self, byte_s):
        if byte_s is not None and len(byte_s) > 0:
            bytes_written = self._circular_io.write(byte_s)
            if self._num_bytes_written < self._buffer_size:
                self._num_bytes_written = min(self._num_bytes_written + bytes_written, self._buffer_size)

    def close():
       self._circular_io.close()

