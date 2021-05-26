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
  level=logging.DEBUG,
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
  KB = 1024
  camera = picamera.PiCamera()
  mp4_file = io.open('./final.mp4', mode='wb', buffering=100*KB)
  ffmpeg_process = subprocess.Popen([
    'ffmpeg', '-i', '-' # receive .h264 from stdin
    ,'-codec', 'copy', '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1' # write .mp4 to stdout
  ], stdin=subprocess.PIPE, stdout=mp4_file, bufsize=5*1024*KB)

  try:
    count = 1

    buffer_stream_1 = io.BufferRandom(io.BytesIO(), buffer_size=10*1024*KB)
    buffer_stream_2 = io.BufferRandom(io.BytesIO(), buffer_size=10*1024*KB)

    # Set the quantization parameter which will cause the video encoder to use VBR (variable bit-rate) encoding.
    # This can be considerably more efficient especially in mostly static scenes (which can be important when recording to memory)
    camera.start_recording(buffer_stream_1, format='h264', quantization=23)
    while True:
      camera.wait_recording(1)
      if buffer_stream_1.tell() > 0:
        buffer_stream_2.seek(0)
        camera.split_recording(buffer_stream_2)
        bytes = buffer_stream_1.read()
      elif buffer_stream_2.tell() > 0:
        buffer_stream_1.seek(0)
        camera.split_recording(buffer_stream_1)
        bytes = buffer_stream_2.read()

      logging.info("read from camera len: %d", len(bytes))
      if bytes: ffmpeg_process.stdin.write(bytes)

      logging.info("count: %d", count)

      if count > 2:
        break
      else:
        count = count + 1
        sleep(1)
  finally:
    camera.stop_recording()
    camera.close()
    if ffmpeg_process.poll() is not None: ffmpeg_process.kill()
    mp4_file.close()

if __name__ == "__main__":
  main()

