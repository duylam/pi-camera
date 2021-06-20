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

        write_content = b'\x03\x04'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, write_content)

        write_content = b'\x05\x06\x07'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 3)
        self.assertEqual(read_bytes, write_content)

    def test_read_behaviors(self):
        stream = CircularStream(buffer_size=3)
        write_content = b'\x01\x02'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertIsNotNone(read_bytes, 'read() should return data')
        read_bytes = stream.read()
        self.assertIsNone(read_bytes)

