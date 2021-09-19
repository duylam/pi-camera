import logging
import queue
import asyncio
from .  import models
from lib import RtcConnection, config

async def run(request: queue.Queue, response: queue.Queue):
    debug_ns = "{}.peer_connection_task".format(config.ROOT_LOGGING_NAMESPACE)
    logger = logging.getLogger(debug_ns)
    logger.info('Starting')

    while True:
        while not request.empty():
            cn = None
            offer = None
            error_msg = None
            client_id = None
            try:
                request_message = request.get_nowait()
                client_id = request_message.client_id
                cn = RtcConnection(client_id)
                offer = await cn.create_offer()
                logger.debug('create-offer SDP: %s' % offer)
            except asyncio.exceptions.CancelledError:
                raise
            except:
                error_msg = str(sys.exc_info()[0])
                logger.exception('Unknown error on handling request, ignore and continue with next item')
            finally:
                response_message = models.CreateRtcConnectionResponse(client_id, pc = cn, sdp_offer = offer, error_msg = error_msg)
                try:
                    response.put_nowait(response_message)
                except:
                    logger.exception('Unknown error on sending response, ignore and continue with next item')

        await asyncio.sleep(0.1)

