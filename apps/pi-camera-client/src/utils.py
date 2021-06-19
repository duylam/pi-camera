import threading
import time
import os
import io

def pipeStream(
    srcStream, desStream,
    autoCloseSrcStreamOnEnd = False, autoCloseDesStreamOnEnd = False,
    chunkSize = 1):
  shouldStop = False

  def waitTillEnd(force = True):
    if force: shouldStop = True
    thread.join()

  def copyChunk():
    while True:
      if srcStream.closed or desStream.closed or shouldStop: break

      bytes = srcStream.read(chunkSize)
      if bytes:
        print("read: %d", len(bytes))

        desStream.write(bytes)
      else:
        print("end: %d", len(bytes))

        if autoCloseSrcStreamOnEnd: break

      time.sleep(0.1)

    if autoCloseSrcStreamOnEnd: srcStream.close()
    if autoCloseDesStreamOnEnd: desStream.close()

  thread = threading.Thread(target=copyChunk)
  thread.start()

  return waitTillEnd

def createCircleStream(bufferSize = 102400):
  readFileId, writeFileId = os.pipe()
  writeStream = io.BufferedWriter(io.FileIO(writeFileId, mode='w'), bufferSize)
  readStream = io.BufferedReader(io.FileIO(readFileId, mode='r'), bufferSize)

  return writeStream, readStream
