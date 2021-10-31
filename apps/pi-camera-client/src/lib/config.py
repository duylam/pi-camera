import os
import logging
from dotenv import load_dotenv

from lib import const

# Take environment variables from .env file for local development
load_dotenv()

GRPC_HOSTNAME = os.getenv('PI_CAMERA_GRPC_HOSTNAME', 'localhost')
GRPC_PORT = int(os.getenv('PI_CAMERA_GRPC_PORT', 4000))

# A comma-separated list of ice server urls
ICE_SERVER_URLS = os.getenv(
    'PI_CAMERA_ICE_SERVER_URLS', 'stun:stun.stunprotocol.org:3478').split(',')

CAMERA_BUFFER_SIZE = int(
    os.getenv('PI_CAMERA_CAMERA_BUFFER_SIZE_IN_KB', 5*1024))*const.KB
ROOT_LOGGING_NAMESPACE = os.getenv(
    'PI_CAMERA_ROOT_LOGGING_NAMESPACE', 'pi_box')

# See https://docs.python.org/3/library/logging.html?highlight=logging#logging-levels
LOG_LEVEL_NUM = int(os.getenv('PI_CAMERA_LOGGING_LEVEL_NUM', logging.DEBUG))

# A comma-separated list of logger names that their log messages will be set
# at WARNING level, this is helpful for developing
QUIET_LOGGER_NAMES = os.getenv('PI_CAMERA_QUIET_LOGGER_NAMES', '')

FRAMERATE = int(os.getenv('PI_CAMERA_FRAME_PER_SECOND', 20))
VIDEO_RESOLUTION_WIDTH = int(os.getenv('PI_CAMERA_VIDEO_RESOLUTION_WIDTH', 640))
VIDEO_RESOLUTION_HEIGHT = int(os.getenv('PI_CAMERA_VIDEO_RESOLUTION_HEIGHT', 480))
VIDEO_RESOLUTION = (VIDEO_RESOLUTION_WIDTH, VIDEO_RESOLUTION_HEIGHT)

# The quantization option for video
# For the 'h264' format, use values between 10 and 40 where 10 is extremely high quality,
# and 40 is extremely low (20-25 is usually a reasonable range for H.264 encoding).
# See https://picamera.readthedocs.io/en/release-1.3/api.html#picamera.PiCamera.start_recording
VIDEO_QUALITY_OPTION = int(os.getenv('PI_CAMERA_VIDEO_QUALITY_OPTION', 30))

# The ICE gathering process takes around 3 seconds per each connection, this env
# define maximum connection in queue for ice gathering process
MAX_CONCURRENT_RTC_ICE_GATHERING_QUEUE = int(
    os.getenv('PI_CAMERA_MAX_CONCURRENT_RTC_ICE_GATHERING_QUEUE', 100))

