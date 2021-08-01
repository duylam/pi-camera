import os
import logging
from dotenv import load_dotenv

from lib import const

# Take environment variables from .env file for local development
load_dotenv()

GRPC_HOSTNAME = os.getenv('PI_MEETING_GRPC_HOSTNAME', 'localhost')
GRPC_PORT = int(os.getenv('PI_MEETING_GRPC_PORT', 4000))
MAIN_TASK_INTERVAL_DURATION = int(
    os.getenv('PI_MEETING_MAIN_TASK_INTERVAL_DURATION_MS', 100))
FRAMERATE = int(os.getenv('PI_MEETING_FRAME_PER_SECOND', 20))
CAMERA_BUFFER_SIZE = int(
    os.getenv('PI_MEETING_CAMERA_BUFFER_SIZE_IN_KB', 5*1024))*const.KB
ROOT_LOGGING_NAMESPACE = os.getenv(
    'PI_MEETING_ROOT_LOGGING_NAMESPACE', 'pi_box')

# See https://docs.python.org/3/library/logging.html?highlight=logging#logging-levels
LOG_LEVEL_NUM = int(os.getenv('PI_MEETING_LOGGING_LEVEL_NUM', logging.DEBUG))

VIDEO_RESOLUTION = (1024, 768)  # (width, height)
