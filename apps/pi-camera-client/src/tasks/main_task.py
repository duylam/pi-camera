from google.protobuf import empty_pb2
from schema_python import rtc_signaling_service_pb2
from lib import RtcConnection, config

WEBRTC_VIDEO_TRACK_BUFFER_SIZE = config.CAMERA_BUFFER_SIZE*4

async def run(
  new_video_chunk_queue,
  incoming_rtc_request_queue,
  outgoing_rtc_response_queue
):
    peer_connections = set()
    try:
        while True:
            closed_peer_connections = filter(lambda c: c.closed, peer_connections)

            # Most of times that the loop is running, connections are usually stay openning. So to
            # avoid to create new set unneccessaily, we keep the set as is if no connection closing
            if len(closed_peer_connections) > 0:
                peer_connections = peer_connections ^ closed_peer_connections

            while not new_video_chunk_queue.empty():
                video_bytes = new_video_chunk_queue.get()
                for pc in peer_connections:
                  if pc.ready:
                    pc.send_video_bytes(video_bytes)

            while not incoming_rtc_request_queue.empty():
                request = incoming_rtc_request_queue.get()
                client_id = request.call_id
                if request.create_offer:
                    cn = RtcConnection(buffer_size=WEBRTC_VIDEO_TRACK_BUFFER_SIZE, client_id = client_id)
                    offer = await cn.create_offer()
                    response = rtc_signaling_service_pb2.RtcSignalingResponse()
                    response.create_offer = offer

                    try:
                        outgoing_rtc_response_queue.put(response, timeout=2)
                        peer_connections.add(cn)
                    except:
                        logging.exception('Error writing to signaling response queue')
                elif request.answer_offer:
                    for c in peer_connections:
                        if c.client_id == client_id:
                            await c.receive_answer(request.answer_offer)
                            break

                    response = rtc_signaling_service_pb2.RtcSignalingResponse()
                    response.answer_offer = empty_pb2.Empty()

                    try:
                        outgoing_rtc_response_queue.put(response, timeout=2)
                    except:
                        logging.exception('Error writing to signaling response queue')
                elif request.confirm_answer:
                    for c in peer_connections:
                        if c.client_id == client_id:
                            c.confirm_answer()
                            break


    except:
        logging.exception('Error on main task, skip to next loop')




