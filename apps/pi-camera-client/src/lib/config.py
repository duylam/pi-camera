import os
import logging
from dotenv import load_dotenv

from lib import const

# Take environment variables from .env file for local development
load_dotenv()

GRPC_HOSTNAME = os.getenv('PI_MEETING_GRPC_HOSTNAME', 'localhost')
GRPC_PORT = int(os.getenv('PI_MEETING_GRPC_PORT', 4000))

# A comma-separated list of ice server urls
ICE_SERVER_URLS = os.getenv(
    'PI_MEETING_ICE_SERVER_URLS', 'stun:stun.stunprotocol.org:3478').split(',')

CAMERA_BUFFER_SIZE = int(
    os.getenv('PI_MEETING_CAMERA_BUFFER_SIZE_IN_KB', 5*1024))*const.KB
ROOT_LOGGING_NAMESPACE = os.getenv(
    'PI_MEETING_ROOT_LOGGING_NAMESPACE', 'pi_box')

# See https://docs.python.org/3/library/logging.html?highlight=logging#logging-levels
LOG_LEVEL_NUM = int(os.getenv('PI_MEETING_LOGGING_LEVEL_NUM', logging.DEBUG))

# A comma-separated list of logger names that their log messages will be set
# at WARNING level, this is helpful for developing
QUIET_LOGGER_NAMES = os.getenv('PI_MEETING_QUIET_LOGGER_NAMES', '')

FRAMERATE = int(os.getenv('PI_MEETING_FRAME_PER_SECOND', 24))
VIDEO_RESOLUTION = (640, 480)  # (width, height)

# The quantization option for video
# For the 'h264' format, use values between 10 and 40 where 10 is extremely high quality,
# and 40 is extremely low (20-25 is usually a reasonable range for H.264 encoding).
# See https://picamera.readthedocs.io/en/release-1.3/api.html#picamera.PiCamera.start_recording
VIDEO_QUALITY_OPTION = int(os.getenv('PI_MEETING_VIDEO_QUALITY_OPTION', 20))
