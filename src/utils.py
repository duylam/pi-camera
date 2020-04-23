import threading
import time

def pipeStream(srcStream, desStream, autoCloseSrcStreamOnEnd = False, autoCloseDesStreamOnEnd = False):
  CHUNK_SIZE = 512
  shouldStop = False

  def waitTillEnd(force = True):
    if force: shouldStop = True
    thread.join()

  def copyChunk():
    while True:
      if srcStream.closed or desStream.closed or shouldStop: break

      bytes = srcStream.read(CHUNK_SIZE)
      if bytes:
        desStream.write(bytes)
      else:
        if autoCloseSrcStreamOnEnd: break

      time.sleep(0.1)

    if autoCloseSrcStreamOnEnd: srcStream.close()
    if autoCloseDesStreamOnEnd: desStream.close()

  thread = threading.Thread(target=copyChunk)
  thread.start()

  return waitTillEnd
