import logging, queue

from lib import Camera

async def run(outgoing_video_chunk_queue: queue.Queue):
    logging.debug('Starting Camera task')

    # Read frame info.
    # See https://picamera.readthedocs.io/en/release-1.13/api_camera.html#pivideoframe
    #video_frame_info = camera.frame
    while True:
        try:
            logging.debug('Initializing Camera module')
            with Camera() as camera:
                logging.debug('Initialized Camera module. Begin loop of capturing camera hardware and sending video chunks to queue')
                while True:
                    await camera.capture_recording()
                    video_frames = camera.get_video_video_frames()
                    if len(video_frames) > 0:
                        try:
                            if outgoing_video_chunk_queue.full():
                                logging.warning('The video queue is full, remove oldest chunk')
                                outgoing_video_chunk_queue.get(block=True,timeout=1)

                            outgoing_video_chunk_queue.put_nowait(video_frames)
                        except KeyboardInterrupt:
                            raise
                        except:
                            logging.exception('Error on writing video chunk to queue, skip the chunk')

        except KeyboardInterrupt:
            raise
        except:
            logging.exception('Camera has fatal error, re-initializing it')

