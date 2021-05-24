import logging
from time import sleep
import threading
import io
import os
import picamera
import subprocess
import time
import utils

# Code gia, k sai khi co camera that
def feedRawVideoStream(outputStream):
  fileReadStream = io.BufferedReader(io.FileIO('./outfile.h264', mode='r'), 102400)
  stop = utils.pipeStream(fileReadStream, outputStream, autoCloseSrcStreamOnEnd = True, autoCloseDesStreamOnEnd = True, chunkSize = 10240)
  return stop

# code gia, code thiet la ghi ra mang
def writeMp4ToFile(inputStream):
  fileWriteStream = io.open('./final.mp4', mode='wb', buffering=1024)
  stop = utils.pipeStream(inputStream, fileWriteStream, autoCloseDesStreamOnEnd = True)
  return stop

def convertToMp4(rawVideoInputStream, mp4OutputStream):
  print('created streams')

  shouldStop = False
  ffmpegStdinRfd, ffmpegStdinWfd = os.pipe()
  ffmpegStdoutRfd, ffmpegStdoutWfd = os.pipe()
  ffmpegStdinStream = io.open(ffmpegStdinWfd, mode='wb', buffering=1024)
  ffmpegStdoutStream = io.open(ffmpegStdoutRfd, mode='rb', buffering=1024)

  ffpmegProcess = subprocess.Popen([
    'ffmpeg', '-v', 'debug', '-i', '-','-codec', 'copy',
    '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1'
  ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

  stopPipingFfpmegStdin = utils.pipeStream(rawVideoInputStream, ffpmegProcess.stdin)
  stopPipingFfpmegStdout = utils.pipeStream(ffpmegProcess.stdout, mp4OutputStream)

  def waitForConverting():
    while True:
      if shouldStop or ffpmegProcess.poll() is not None: break
      time.sleep(0.5)

    if ffpmegProcess.poll() is not None: ffpmegProcess.kill()
    cleanUp()

  thread = threading.Thread(target=waitForConverting)

  def waitUtilCompletion(forceStop = False):
    if forceStop: shouldStop = True
    thread.join()
    cleanUp()
    stopPipingFfpmegStdin(forceStop)
    stopPipingFfpmegStdout(forceStop)

  def cleanUp():
    ffmpegStdinStream.close()
    ffmpegStdoutStream.close()
    os.close(ffmpegStdinRfd)
    os.close(ffmpegStdinWfd)
    os.close(ffmpegStdoutRfd)
    os.close(ffmpegStdoutWfd)

  thread.start()

  return waitUtilCompletion

logging.basicConfig(
  format="%(asctime)s: %(message)s",
  level=logging.INFO,
  datefmt="%H:%M:%S")

rawVideoStream = io.BytesIO()
mp4VideoStream = io.BytesIO()

#try:
#  writeStream, readStream = utils.createCircleStream()
#
#  # logging.info("Starting threads")
#  # waitTillEnd1 = feedRawVideoStream(rawVideoStream)
#  waitTillEnd1 = feedRawVideoStream(writeStream)
#
#  while True:
#    bytes = readStream.read(102400)
#    if bytes:
#      logging.info("read2 100: %d", len(bytes))
#    else:
#      logging.info("read2")
#      break
#
#  logging.info("done")
#
#  # waitTillEnd2 = convertToMp4(rawVideoStream, mp4VideoStream)
#  # waitTillEnd3 = writeMp4ToFile(mp4VideoStream)
#
#  # # dummy code, k su dung khi co stream tu picamera
#  # print('waiting for reading file')
#  # waitTillEnd1(False)
#
#  # print('Read file done, waiting for convering')
#
#  # waitTillEnd2(False)
#
#  # print('Convering done, waiting for writing')
#
#  # mp4VideoStream.close()
#  # waitTillEnd3(False)
#
#except KeyboardInterrupt:
#  print 'a'
#  # waitTillEnd1(True)
#  # waitTillEnd2(True)
#  # waitTillEnd3(True)


def main():
  camera = picamera.PiCamera()
  ffmpeg_process = subprocess.Popen([
    'ffmpeg', '-v', 'debug', '-i', '-' # receive .h264 from stdin
    ,'-codec', 'copy', '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1' # write .mp4 to stdout
  ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=5*1024*1024)
  mp4_file = io.open('./final.mp4', mode='wb', buffering=1024*1024)

  try:
    count = 1

    # See doc https://picamera.readthedocs.io/en/release-1.13/api_streams.html#circulario
    buffer_stream = picamera.CircularIO(10*1024*1024)
    camera.start_recording(buffer_stream, format='h264')
    sleep(1) # make sure the buffer not empty
    while True:
      bytes = buffer_stream.read()
      if bytes: ffmpeg_process.stdin.write(bytes)

      bytes = ffmpeg_process.stdout.read()
      if bytes: mp4_file.write(bytes)

      if count > 3:
        break
      else:
        ++count
        sleep(5)
  finally:
    camera.stop_recording()
    if ffpmegProcess.poll() is not None: ffpmegProcess.kill()
    mp4_file.close()

if __name__ == "__main__":
  main()

