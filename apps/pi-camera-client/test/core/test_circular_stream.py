import unittest

from core import CircularStream

class TestCircularStream(unittest.TestCase):
    def test_write_below_buffer_size(self):
        stream = CircularStream(buffer_size=5)
        write_content = b'\x01\x02'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertIsNotNone(read_bytes)
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, write_content)

    def test_multi_write_below_buffer_size(self):
        stream = CircularStream(buffer_size=5)
        stream.write_(b'\x01\x02')
        stream.read()
        write_content = b'\x03\x04'
        stream.write_(write_content)
        read_bytes = stream.read()
        self.assertIsNotNone(read_bytes)
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, write_content)

    def test_multi_write_over_buffer_size(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02\x03\x04')
        stream.write_(b'\x05\x06')
        read_bytes = stream.read()
        self.assertIsNotNone(read_bytes)
        self.assertEqual(len(read_bytes), 3)
        self.assertEqual(read_bytes, b'\x04\x05\x06')

    def test_read_all_when_empty(self):
        stream = CircularStream(buffer_size=3)
        self.assertIsNone(stream.read())

    def test_read_all_when_unavailale(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02')
        stream.read()
        self.assertIsNone(stream.read())

    def test_read_num_when_unavailale(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02')
        stream.read()
        self.assertIsNone(stream.read(1))

    def test_read_num_when_empty(self):
        stream = CircularStream(buffer_size=3)
        self.assertIsNone(stream.read(1))

    def test_read_all_when_availale(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01')
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 1)
        self.assertEqual(read_bytes, b'\x01')

        stream.write_(b'\x02')
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 1)
        self.assertEqual(read_bytes, b'\x02')

    def test_read_num_when_availale(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02')
        read_bytes = stream.read(1)
        self.assertEqual(len(read_bytes), 1)
        self.assertEqual(read_bytes, b'\x01')

        read_bytes = stream.read(1)
        self.assertEqual(len(read_bytes), 1)
        self.assertEqual(read_bytes, b'\x02')

    def test_read_over_num_when_availale(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02')
        read_bytes = stream.read(3)
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, b'\x01\x02')

    def test_read_all_over_buffer_size_when_available(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02\x03\x04\x05')
        read_bytes = stream.read()
        self.assertEqual(len(read_bytes), 3)
        self.assertEqual(read_bytes, b'\x03\x04\x05')

    def test_read_num_over_buffer_size_when_available(self):
        stream = CircularStream(buffer_size=3)
        stream.write_(b'\x01\x02\x03\x04\x05')
        read_bytes = stream.read(1)
        self.assertEqual(len(read_bytes), 1)
        self.assertEqual(read_bytes, b'\x03')

        read_bytes = stream.read(2)
        self.assertEqual(len(read_bytes), 2)
        self.assertEqual(read_bytes, b'\x04\x05')

