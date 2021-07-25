import logging, queue, asyncio

from lib import Camera, config

async def run(outgoing_video_chunk_queue: queue.Queue):
    logger = logging.getLogger("{}.camera_task".format(config.ROOT_LOGGING_NAMESPACE))
    logger.info('Starting')

    while True:
        try:
            logger.info('Initializing Camera module')
            with Camera() as camera:
                logger.info('Initialized Camera module. Started loop of capturing camera data')
                while True:
                    await camera.capture_recording()
                    video_frames = camera.get_video_video_frames()
                    if len(video_frames) > 0:
                        try:
                            if outgoing_video_chunk_queue.full():
                                logger.debug('The video queue is full, remove oldest chunk')
                                outgoing_video_chunk_queue.get_nowait()

                            outgoing_video_chunk_queue.put_nowait(video_frames)
                        except:
                            logger.exception('Error on writing video frames to queue, discarded this batch of frames')

        except asyncio.exceptions.CancelledError:
            raise
        except:
            logger.exception('Camera module has fatal error, re-initializing it after 2s')
            await asyncio.sleep(2)

