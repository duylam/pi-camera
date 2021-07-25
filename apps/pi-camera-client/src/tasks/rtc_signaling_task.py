import grpc, logging, queue, asyncio

from typing import Iterable
from schema_python import rtc_signaling_service_pb2_grpc, rtc_signaling_service_pb2

from lib import config

async def run(request_queue: queue.Queue, response_queue: queue.Queue):
    logger = logging.getLogger("{}.rtc_task".format(config.ROOT_LOGGING_NAMESPACE))

    # See sample code at https://github.com/grpc/grpc/blob/fd3bd70939fb4239639fbd26143ec416366e4157/examples/python/route_guide/asyncio_route_guide_server.py#L111
    async def send_response() -> Iterable[rtc_signaling_service_pb2.RtcSignalingMessage]:
        while True:
            try:
                while not response_queue.empty():
                    res = response_queue.get_nowait()
                    yield res

                await asyncio.sleep(0.1)
            except asyncio.exceptions.CancelledError:
                raise
            except:
                pass

    logger.info('Starting')
    grpc_server_origin="{0}:{1}".format(config.GRPC_HOSTNAME, config.GRPC_PORT)
    while True:
        try:
            logger.info('Creating GRPC client stub')
            async with grpc.aio.insecure_channel(grpc_server_origin) as channel:
                grpc_client = rtc_signaling_service_pb2_grpc.RtcSignalingStub(channel)
                logger.info('Created GRPC client stub')
                message_stream = grpc_client.SubscribeMessage(send_response())
                logger.info('Connected with Signaling server, begin receiving stream')
                async for msg in message_stream:
                    if msg.WhichOneof('type') == 'noop':
                        continue

                    if request_queue.full():
                        logger.warning('incoming_message_queue is full, skip this message')
                        continue

                    try:
                        request_queue.put_nowait(msg)
                    except:
                        logger.exception('Error on writing to request_queue')
        except asyncio.exceptions.CancelledError:
            raise
        except:
            logger.exception('GRCP stream has error, reconnect again after 5s')
            await asyncio.sleep(5)

