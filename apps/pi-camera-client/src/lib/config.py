import os
import const

GRPC_HOSTNAME=os.getenv('PI_MEETING_GRPC_HOSTNAME', 'localhost')
GRPC_PORT=os.getenv('PI_MEETING_GRPC_PORT', 4000)

VIDEO_RESOLUTION = (1024, 768) # (width, height)
FRAMERATE = 20
CAMERA_BUFFER_SIZE = 5*1024*const.KB

