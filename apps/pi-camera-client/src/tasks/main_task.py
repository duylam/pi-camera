import logging, asyncio
from google.protobuf import empty_pb2
from schema_python import rtc_signaling_service_pb2
from lib import RtcConnection, config

async def run(
  new_video_chunk_queue,
  incoming_rtc_request_queue,
  outgoing_rtc_response_queue
):
    WEBRTC_VIDEO_TRACK_BUFFER_SIZE = config.CAMERA_BUFFER_SIZE*4

    logging.debug('Starting Main task')
    peer_connections = set([])
    sleep_in_second = config.MAIN_TASK_INTERVAL_DURATION / 1000
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
                request = incoming_rtc_request_queue.get()
                client_id = request.call_id
                logging.debug("Request payload: {}".format(request.__str__()))
                if request.WhichOneof('type') == 'create_offer':
                    response = rtc_signaling_service_pb2.RtcSignalingResponse()
                    try:
                      cn = RtcConnection(client_id)
                      offer = await cn.create_offer()
                      response.create_offer = offer
                    except KeyboardInterrupt:
                      raise
                    except:
                      response.error = True
                      logging.exception('Error on creating RTC connection')

                    try:
                        outgoing_rtc_response_queue.put(response, timeout=2)
                        logging.debug('Dispatched SDP of create_offer to queue')
                        if not response.error:
                          peer_connections.add(cn)
                    except KeyboardInterrupt:
                      raise
                    except:
                        logging.exception('Error writing to signaling response queue')
                elif request.WhichOneof('type') == 'answer_offer':
                    response = rtc_signaling_service_pb2.RtcSignalingResponse()
                    response.answer_offer.CopyFrom(empty_pb2.Empty())
                    for c in peer_connections:
                        if c.client_id == client_id:
                          try:
                            await c.receive_answer(request.answer_offer)
                          except KeyboardInterrupt:
                            raise
                          except:
                            response.error = True
                            logging.exception('Error on procesing RTC answer')
                          finally:
                            break

                    try:
                        outgoing_rtc_response_queue.put(response, timeout=2)
                        logging.debug('Dispatched confirmation to queue')
                    except KeyboardInterrupt:
                      raise
                    except:
                        logging.exception('Error writing to signaling response queue')
                elif request.WhichOneof('type') == 'ice_candidate':
                    for c in peer_connections:
                        if c.client_id == client_id:
                          try:
                            await c.add_ice_candidate(request.ice_candidate)
                          except KeyboardInterrupt:
                            raise
                          except:
                            logging.exception('Error on procesing ICE candidate')
                          finally:
                            break

                elif request.WhichOneof('type') == 'confirm_answer':
                    for c in peer_connections:
                        if c.client_id == client_id:
                            c.confirm_answer()
                            break

            await asyncio.sleep(sleep_in_second)

    except KeyboardInterrupt:
      raise
    except:
        logging.exception('Error on main task, skip to next loop')




