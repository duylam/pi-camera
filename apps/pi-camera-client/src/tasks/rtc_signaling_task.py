import grpc, logging, queue, asyncio
from typing import Iterable
from schema_python import rtc_signaling_service_pb2_grpc, rtc_signaling_service_pb2

from lib import config

async def run(request_queue: queue.Queue, response_queue: queue.Queue):
    # See sample code at https://github.com/grpc/grpc/blob/fd3bd70939fb4239639fbd26143ec416366e4157/examples/python/route_guide/asyncio_route_guide_server.py#L111
    async def send_response() -> Iterable[rtc_signaling_service_pb2.RtcSignalingMessage]:
        while True:
            try:
                while not response_queue.empty():
                    res = response_queue.get()
                    yield res

                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                raise
            except:
                pass

    logging.debug('Starting RTC Connection task')
    grpc_server_origin="{0}:{1}".format(config.GRPC_HOSTNAME, config.GRPC_PORT)
    while True:
        try:
            async with grpc.aio.insecure_channel(grpc_server_origin) as channel:
                grpc_client = rtc_signaling_service_pb2_grpc.RtcSignalingStub(channel)
                logging.debug('Created GRPC client stub')
                message_stream = grpc_client.SubscribeMessage(send_response())
                logging.debug('Connected with Signaling server, begin receiving stream')
                async for msg in message_stream:
                    if msg.WhichOneof('type') == 'noop':
                        continue

                    if request_queue.full():
                        logging.warning('request_qeuue is full, skip the message')
                        continue

                    try:
                        request_queue.put_nowait(msg)
                    except KeyboardInterrupt:
                      raise
                    except:
                        logging.exception('Error on writing to request_queue')
        except KeyboardInterrupt:
            raise
        except:
            logging.exception('Error stream, reconnect again after 5s')
            await asyncio.sleep(5)

