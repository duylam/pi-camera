import logging, asyncio
from google.protobuf import empty_pb2
from schema_python import rtc_signaling_service_pb2
from lib import RtcConnection, config

GOOGLE_EMPTY = empty_pb2.Empty()

async def run(
  new_video_chunk_queue,
  incoming_rtc_request_queue,
  outgoing_rtc_response_queue
):
    WEBRTC_VIDEO_TRACK_BUFFER_SIZE = config.CAMERA_BUFFER_SIZE*4

    logging.debug('Starting Main task')
    peer_connections = set([])
    sleep_in_second = config.MAIN_TASK_INTERVAL_DURATION / 1000
    noop_msg = rtc_signaling_service_pb2.RtcSignalingMessage()
    noop_msg.noop.CopyFrom(GOOGLE_EMPTY)
    try:
        logging.debug('Begin loop of forwarding video chunk to peer connections')
        while True:
            # TODO: add timestamp of created time and auto remove peer connection with state
            # non connected since UDP doesn't know the other peer (browser) refreshes
            closed_peer_connections = set(filter(lambda c: (c.closed), peer_connections))

            # Most of times that the loop is running, connections are usually stay openning. So to
            # avoid to create new set unneccessaily, we keep the set as is if no connection closing
            if len(closed_peer_connections) > 0:
                logging.debug('Found closed peer connection, removing them')
                peer_connections = peer_connections ^ closed_peer_connections

            while not new_video_chunk_queue.empty():
                video_frames = new_video_chunk_queue.get()
                for pc in peer_connections:
                  if pc.ready:
                    pc.append_video_frames(video_frames)

            while not incoming_rtc_request_queue.empty():
                incoming_msg = incoming_rtc_request_queue.get()
                if not incoming_msg.WhichOneof('request'):
                    logging.debug('Expect .request field, skip the message')

                request = incoming_msg.request
                logging.debug("Request payload: {}".format(request.__str__()))

                if not request.HasField('call_header'):
                    logging.debug('Expect .request.call_header field, skip the message')
                    continue

                client_id = request.call_header.client_id
                if not client_id:
                    logging.debug('Expect .request.call_header.client_id field, skip the message')
                    continue

                if request.WhichOneof('type') == 'create_offer':
                    err_msg = None
                    offer = None
                    try:
                      cn = RtcConnection(client_id)
                      offer = await cn.create_offer()
                      peer_connections.add(cn)
                    except:
                      err_msg = str(sys.exc_info()[0])
                      logging.exception('Error on creating RTC connection')
                    finally:
                      try:
                          msg = get_message_response_create_offer(client_id,create_offer=offer, err_msg=err_msg)
                          outgoing_rtc_response_queue.put(msg, timeout=2)
                          logging.debug('Dispatched SDP of create_offer to queue')
                      except:
                          logging.exception('Error writing to signaling response queue')
                elif request.WhichOneof('type') == 'answer_offer':
                    err_msg = None
                    for c in peer_connections:
                        if c.client_id == client_id:
                          try:
                            await c.receive_answer(request.answer_offer)
                          except:
                            err_msg = str(sys.exc_info()[0])
                            logging.exception('Error on procesing RTC answer')
                          finally:
                            break

                    try:
                        outgoing_rtc_response_queue.put(get_message_response_answer_offer(client_id, err_msg), timeout=2)
                        logging.debug('Dispatched confirmation to queue')
                    except:
                        logging.exception('Error writing to signaling response queue')
                elif request.WhichOneof('type') == 'ice_candidate':
                    for c in peer_connections:
                        if c.client_id == client_id:
                          try:
                            await c.add_ice_candidate(request.ice_candidate)
                          except:
                            logging.exception('Error on procesing ICE candidate')
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
            except:
                logging.exception('Warning: failed to send hearthbeat message')

            await asyncio.sleep(sleep_in_second)

    except KeyboardInterrupt:
      raise
    except:
        logging.exception('Error on main task, skip to next loop')

def get_message_response_create_offer(client_id, create_offer, err_msg = None):
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

def get_message_response_answer_offer(client_id, err_msg = None):
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

