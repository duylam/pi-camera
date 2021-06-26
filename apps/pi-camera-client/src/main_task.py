async def run(
  new_video_chunk_queue,
  incoming_rtc_request_queue,
  outgoing_rtc_response_queue
):
    peer_connections = set()




      closed_peer_connections = filter(lambda c: c.closed, peer_connections)

      # Most of times that the loop is running, connections are usually stay openning. So to
      # avoid to create new set unneccessaily, we keep the set as is if no connection closing
      if len(closed_peer_connections) > 0:
          peer_connections = peer_connections ^ closed_peer_connections

      for pc in peer_connections:
        pc.send_video_bytes(video_bytes)
