import unittest

from core import CircularStream

class TestCircularStream(unittest.TestCase):
    def test_write_(self):
        stream = CircularStream(buffer_size=5)
        write_content = b'\x01\x02'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertIsNotNone(read_bytes, 'read() should return data')
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, write_content)

        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02\x03\x04\x05')
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 3)
        self.assertEqual(read_bytes, b'\x03\x04\x05')

    def test_read_when_writing_once(self):
        True


    def test_read_when_writing_cicle(self):
        True

