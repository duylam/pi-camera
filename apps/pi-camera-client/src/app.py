import sys
import os

# The proto compiler for Python language is designed for Python 2 import mechanics.
# Per the comment at https://github.com/protocolbuffers/protobuf/issues/1491#issuecomment-772720912,
# the change in sys.path below is a workaroud for Python 3
sys.path.append(os.path.join(os.path.dirname(__file__), 'schema_python'))

import asyncio
import logging
import types
from tasks import run_camera, run_rtc_signaling, run_main, run_peer_connection
from queue import Queue
from lib import config

logging.basicConfig(
    # Format at https://docs.python.org/3/library/logging.html?highlight=logging#logrecord-attributes
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",

    # Depress debug log from other modules by default
    level=config.LOG_LEVEL_NUM)
root_logger = logging.getLogger(config.ROOT_LOGGING_NAMESPACE)

def print_envs():
    root_logger.info("Env vars:")
    for attr_name in dir(config):
        if not attr_name.startswith('__'):
            attr_value = getattr(config, attr_name)
            if type(attr_value) not in (types.FunctionType, types.LambdaType, types.MethodType, types.ModuleType):
                root_logger.info("- %s=%s", attr_name, attr_value)


def config_logging():
    for name in config.QUIET_LOGGER_NAMES.split(','):
        if name:
            root_logger.info(name)
            logging.getLogger(name).setLevel(logging.WARNING)


async def main():
    config_logging()
    print_envs()

    new_video_chunk_queue = Queue(20)
    incoming_rtc_request_queue = Queue(50)
    outgoing_rtc_response_queue = Queue(50)
    peer_connection_request = Queue(config.MAX_CONCURRENT_RTC_ICE_GATHERING_QUEUE)
    peer_connection_response = Queue(config.MAX_CONCURRENT_RTC_ICE_GATHERING_QUEUE)

    try:
        root_logger.info('Starting top-level tasks')
        await asyncio.gather(
            run_camera(outgoing_video_chunk_queue=new_video_chunk_queue),
            run_rtc_signaling(
                request_queue=incoming_rtc_request_queue,
                response_queue=outgoing_rtc_response_queue
            ),
            run_peer_connection(
                request = peer_connection_request,
                response = peer_connection_response
            ),
            run_main(
                new_video_chunk_queue=new_video_chunk_queue,
                incoming_rtc_request_queue=incoming_rtc_request_queue,
                outgoing_rtc_response_queue=outgoing_rtc_response_queue,
                peer_connection_request = peer_connection_request,
                peer_connection_response = peer_connection_response
            )
        )
    except KeyboardInterrupt:
        root_logger.debug('Received Ctrl-C, exiting')
    except:
        root_logger.exception('Fatal exception, stop app')

if __name__ == "__main__":
    asyncio.run(main())
