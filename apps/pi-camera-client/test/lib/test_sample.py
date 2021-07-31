import unittest

from lib import config


class TestSample(unittest.TestCase):
    def test_ok(self):
        self.assertIsNotNone(config.GRPC_HOSTNAME)
