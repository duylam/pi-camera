import logging
import asyncio
import queue

from google.protobuf import empty_pb2
from schema_python import rtc_signaling_service_pb2
from lib import RtcConnection, config
from tasks.peer_connection_task import models as peer_connection_task_models

GOOGLE_EMPTY = empty_pb2.Empty()

# The interval duration needs to make sure for sending video frames
# with expected rates
INTERVAL_LOOP_MS = 1000 / config.FRAMERATE


async def run(
    new_video_chunk_queue: queue.Queue,
    incoming_rtc_request_queue: queue.Queue,
    outgoing_rtc_response_queue: queue.Queue,
    peer_connection_request: queue.Queue,
    peer_connection_response: queue.Queue
):
    debug_ns = "{}.main_task".format(config.ROOT_LOGGING_NAMESPACE)
    logger = logging.getLogger(debug_ns)

    WEBRTC_VIDEO_TRACK_BUFFER_SIZE = config.CAMERA_BUFFER_SIZE*4

    peer_connections = set([])
    sleep_in_second = INTERVAL_LOOP_MS / 1000
    noop_msg = rtc_signaling_service_pb2.RtcSignalingMessage()
    noop_msg.noop.CopyFrom(GOOGLE_EMPTY)
    logger.info('Started')
    while True:
        logger.info('Started loop')
        try:
            while True:
                closed_peer_connections = set(
                    filter(lambda c: (c.closed), peer_connections))

                # Most of times that the loop is running, connections are usually stay openning. So to
                # avoid to create new set unneccessaily, we keep the set as is if no connection closing
                closed_peer_connections_count = len(closed_peer_connections)
                if closed_peer_connections_count > 0:
                    logger.debug("Found %s closed peer connections",
                                 closed_peer_connections_count)
                    for pc in peer_connections:
                        logger.debug("Closing peer id %s", pc.client_id)
                        await pc.close()

                    logger.debug('Removing closed peer connections')
                    peer_connections = peer_connections ^ closed_peer_connections

                while not new_video_chunk_queue.empty():
                    try:
                        video_frames = new_video_chunk_queue.get_nowait()
                        for pc in peer_connections:
                            if pc.ready:
                                pc.append_video_frames(video_frames)
                    except asyncio.exceptions.CancelledError:
                        raise
                    except:
                        logger.exception(
                            '[WARNING] Error on sending a batch of video frames to peer connections. Continue to next batch')

                while not peer_connection_response.empty():
                    try:
                        peer_connection_response_message = peer_connection_response.get_nowait()
                        err_msg = peer_connection_response_message.error_msg
                        create_offer = None

                        if err_msg is None:
                            logger.debug("Adding new peer connection client_id=%s to list" %
                                         peer_connection_response_message.client_id)
                            peer_connections.add(
                                peer_connection_response_message.pc)
                            create_offer = peer_connection_response_message.sdp_offer

                        msg = get_message_response_create_offer(
                            peer_connection_response_message.client_id, create_offer=create_offer, err_msg=err_msg)
                        outgoing_rtc_response_queue.put_nowait(msg)
                        logger.debug("Dispatched SDP of create_offer for client_id=%s to queue" %
                                     peer_connection_response_message.client_id)
                    except asyncio.exceptions.CancelledError:
                        raise
                    except:
                        logger.exception(
                            '[WARNING] Error on handling peer_connection_response queue item. Continue to next item')

                while not incoming_rtc_request_queue.empty():
                    incoming_msg = incoming_rtc_request_queue.get()
                    if not incoming_msg.WhichOneof('type') == 'request':
                        logger.debug('Expect .request field, skip the message')

                    request = incoming_msg.request
                    logger.debug(
                        "Request payload: {}".format(request.__str__()))

                    if not request.HasField('call_header'):
                        logger.debug(
                            'Expect .request.call_header field, skip the message')
                        continue

                    client_id = request.call_header.client_id
                    if not client_id:
                        logger.debug(
                            'Expect .request.call_header.client_id field, skip the message')
                        continue

                    if request.WhichOneof('type') == 'create_offer':
                        peer_connection_request_message = peer_connection_task_models.CreateRtcConnectionRequest(
                            client_id)
                        try:
                            peer_connection_request.put(
                                peer_connection_request_message, timeout=0.05)
                        except:
                            logger.exception(
                                "Error on processing create_offer for client_id %s. Ignore" % client_id)
                    elif request.WhichOneof('type') == 'answer_offer':
                        err_msg = None
                        for c in peer_connections:
                            if c.client_id == client_id:
                                try:
                                    await c.receive_answer(request.answer_offer)
                                except asyncio.exceptions.CancelledError:
                                    raise
                                except:
                                    err_msg = str(sys.exc_info()[0])
                                    logger.exception(
                                        'Error on procesing RTC answer')
                                finally:
                                    break

                        try:
                            outgoing_rtc_response_queue.put(
                                get_message_response_answer_offer(client_id, err_msg), timeout=2)
                            logger.debug('Dispatched confirmation to queue')
                        except asyncio.exceptions.CancelledError:
                            raise
                        except:
                            logger.exception(
                                'Error writing to signaling response queue')
                    elif request.WhichOneof('type') == 'ice_candidate':
                        for c in peer_connections:
                            if c.client_id == client_id:
                                try:
                                    await c.add_ice_candidate(request.ice_candidate)
                                except asyncio.exceptions.CancelledError:
                                    raise
                                except:
                                    logger.exception(
                                        'Error on procesing ICE candidate')
                                finally:
                                    break

                    elif request.WhichOneof('type') == 'confirm_answer':
                        for c in peer_connections:
                            if c.client_id == client_id:
                                c.confirm_answer()
                                break

                try:
                    # Send heartbeat to detect disconnected network
                    outgoing_rtc_response_queue.put(noop_msg)
                except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
                    raise
                except:
                    logger.exception(
                        'Warning: Failed to send heartbeat message')

                await asyncio.sleep(sleep_in_second)

        except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
            raise
        except:
            logger.exception('Fatal error, skip to next loop')


def get_message_response_create_offer(client_id, create_offer, err_msg=None):
    call_header = rtc_signaling_service_pb2.CallHeader()
    call_header.client_id = client_id
    response = rtc_signaling_service_pb2.RtcSignalingMessage.Response()
    response.call_header.CopyFrom(call_header)

    if err_msg:
        err = rtc_signaling_service_pb2.RtcSignalingMessage.Response.Error()
        err.error_message = err_msg
        response.error.CopyFrom(err)
    else:
        response.create_offer = create_offer

    message = rtc_signaling_service_pb2.RtcSignalingMessage()
    message.response.CopyFrom(response)
    return message


def get_message_response_answer_offer(client_id, err_msg=None):
    call_header = rtc_signaling_service_pb2.CallHeader()
    call_header.client_id = client_id
    response = rtc_signaling_service_pb2.RtcSignalingMessage.Response()
    response.call_header.CopyFrom(call_header)

    if err_msg:
        err = rtc_signaling_service_pb2.RtcSignalingMessage.Response.Error()
        err.error_message = err_msg
        response.error.CopyFrom(err)
    else:
        response.answer_offer.CopyFrom(GOOGLE_EMPTY)

    message = rtc_signaling_service_pb2.RtcSignalingMessage()
    message.response.CopyFrom(response)
    return message
