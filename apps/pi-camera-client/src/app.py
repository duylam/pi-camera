import sys, os

# The proto compiler for Python language is designed for Python 2 import mechanics.
# Per the comment at https://github.com/protocolbuffers/protobuf/issues/1491#issuecomment-772720912,
# the change in sys.path below is a workaroud for Python 3
sys.path.append(os.path.join(os.path.dirname(__file__), 'schema_python'))

# Take environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

import logging, asyncio
from lib import config
from queue import Queue
from tasks import run_camera, run_rtc_signaling, run_main

# TODO:
# 1. Add namespace for component
# 2. Clean up log message
# 3. Make sure the python runs as long-running process (auto healing)
logging.basicConfig(
  format="%(asctime)s [%(levelname)s]: %(message)s",
  level=logging.DEBUG,
  datefmt="%H:%M:%S")

def print_envs():
   logging.info("Env vars:")
   for attr_name in dir(config):
       if not attr_name.startswith('__'):
           attr_value = getattr(config, attr_name)
           if type(attr_value) in (int, str):
               logging.info("- %s=%s", attr_name, attr_value)

async def main():
  print_envs()
  new_video_chunk_queue = Queue(20)
  incoming_rtc_request_queue = Queue(50)
  outgoing_rtc_response_queue = Queue(50)

  try:
    logging.debug('Starting tasks')
    await asyncio.gather(
        run_camera(outgoing_video_chunk_queue=new_video_chunk_queue),
        run_rtc_signaling(
            request_queue=incoming_rtc_request_queue,
            response_queue=outgoing_rtc_response_queue
        ),
        run_main(
            new_video_chunk_queue=new_video_chunk_queue,
            incoming_rtc_request_queue=incoming_rtc_request_queue,
            outgoing_rtc_response_queue=outgoing_rtc_response_queue
        )
    )
  except KeyboardInterrupt:
    logging.debug('Received exit, exiting')
  except:
    logging.exception('Fatal exception')

if __name__ == "__main__":
  asyncio.run(main())

