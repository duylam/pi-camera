import grpc, logging, queue
from typing import AsyncIterable
from schema_python import rtc_signaling_service_pb2_grpc, rtc_signaling_service_pb2

from lib import config

async def run(request_queue: queue.Queue, response_queue: queue.Queue):
    grpc_server_origin="{0}:{1]".format(config.GRPC_HOSTNAME, config.GRPC_PORT)
    async with grpc.aio.insecure_channel(grpc_server_origin) as channel:
        grpc_client = rtc_signaling_service_pb2_grpc.RtcSignalingStub(channel)
        while True:
            try:
                request_stream = grpc_client.Subscribe(send_response())
                async for req in request_streams:
                    continue if req.noop is not None
                    if request_queue.full():
                        logging.warning('request_qeuue is full, skip the message')
                        continue
                    try
                        request_queue.put_nowait(req)
                    except:
                        logging.exception('Error on writing to request_queue')
            except:
                logging.exception('Error stream, reconnect again after 5s')
                await asyncio.sleep(5)

    async def send_response() -> AsyncIterable[rtc_signaling_service_pb2.RtcSignalingResponse]:
        while True:
            while not response_queue.empty():
                yield response_queue.get()

            await asyncio.sleep(0.1)

