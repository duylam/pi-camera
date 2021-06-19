from picamera import PiCamera
from time import sleep

camera = PiCamera()

print('Begin recording ...')

camera.start_preview()
camera.start_recording('./recording-video.h264')
sleep(5)
camera.stop_recording()
camera.stop_preview()

print('Stopped recording. Please check new file in poc/')

