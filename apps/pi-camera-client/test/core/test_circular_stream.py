import unittest

from core import CircularStream

class TestCircularStream(unittest.TestCase):
    def test_ok(self):
        stream = CircularStream()
        self.assertEqual('foo'.upper(), 'FOO')

