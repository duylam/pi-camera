import grpc, logging, queue, asyncio
from typing import AsyncIterable, Iterable
from schema_python import rtc_signaling_service_pb2_grpc, rtc_signaling_service_pb2

from lib import config

async def run(request_queue: queue.Queue, response_queue: queue.Queue):
    # See sample code at https://github.com/grpc/grpc/blob/fd3bd70939fb4239639fbd26143ec416366e4157/examples/python/route_guide/asyncio_route_guide_server.py#L111
    async def send_response() -> Iterable[rtc_signaling_service_pb2.RtcSignalingResponse]:
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
                # See sample code at https://github.com/grpc/grpc/blob/8db79e2e71306a6287ef4223bbf34be3a820e537/examples/python/route_guide/asyncio_route_guide_client.py#L107
                request_stream = grpc_client.Subscribe(send_response())
                logging.debug('Connected with Signaling server, begin receiving stream')
                async for req in request_stream:
                    # See https://developers.google.com/protocol-buffers/docs/reference/python-generated#singular-fields-proto2
                    if req.HasField('noop'):
                        continue

                    logging.debug('received from grpc request')
                    logging.debug(req)

                    if request_queue.full():
                        logging.warning('request_qeuue is full, skip the message')
                        continue

                    try:
                        request_queue.put_nowait(req)
                    except KeyboardInterrupt:
                      raise
                    except:
                        logging.exception('Error on writing to request_queue')
        except KeyboardInterrupt:
            raise
        except:
            logging.exception('Error stream, reconnect again after 5s')
            await asyncio.sleep(5)

