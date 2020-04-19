import logging
import threading
import io
import subprocess
import time

# Code gia, k sai khi co camera that
def feed_raw_video_stream(output_stream):
  FILE_READ_CHUNK_SIZE=1024
  FILE_BUFFER_SIZE=FILE_READ_CHUNK_SIZE*3
  file_read_stream = io.open('./outfile.h264', mode='rb', buffering=FILE_BUFFER_SIZE)

  bytes = file.read(FILE_READ_CHUNK_SIZE)
  while bytes:
    output_stream.write(bytes)
    bytes = file.read(FILE_READ_CHUNK_SIZE)

  file_read_stream.close()
  return;

# code gia, code thiet la ghi ra mang
def write_mp4_to_file(input_stream, exit_event):
  FILE_BUFFER_SIZE=1024
  file_write_stream = io.open('./final.mp4', mode='wb', buffering=FILE_BUFFER_SIZE)

  bytes = input_stream.read(FILE_BUFFER_SIZE)
  while True:
    if bytes:
      file_write_stream.write(bytes)
    else:
      if exit_event.isSet():
        break
      time.sleep(1)
    bytes = input_stream.read(FILE_BUFFER_SIZE)

  file_write_stream.close()
  return;

def convert_to_mp4(raw_video_input_stream, mp4_output_stream):
  CHUNK_SIZE=1024

  def forward_stream(source_stream, dst_stream, exit_even):
    bytes = source_stream.read(CHUNK_SIZE)
    while True:
      if bytes:
        dst_stream.write(bytes)
      else:
        if exit_even.isSet():
          break
        time.sleep(1)
      bytes = source_stream.read(CHUNK_SIZE)

  fifo_file_write_stream = io.open('./ffmpeg-in.fifo', mode='ab', buffering=CHUNK_SIZE)
  fifo_file_mp4_stream = io.open('./ffmpeg-out.fifo', mode='rb', buffering=CHUNK_SIZE)
  ffpmeg_process=subprocess.Popen(
    [
      'ffmpeg', '-i', 'ffmpeg-in.fifo', # todo: need to create pipe file in runtime
      '-codec copy',
      '-movflags frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
      '-f mp4 pipe:1 > ffmpeg-out.fifo'
    ])

  exit_event = threading.Event()
  forward_stream_thread = threading.Thread(target=forward_stream, args=(fifo_file_mp4_stream, mp4_output_stream, exit_event))
  forward_stream_thread.start()

  bytes = raw_video_input_stream.read(CHUNK_SIZE)
  while bytes:
    fifo_file_write_stream.write(bytes)
    bytes = raw_video_input_stream.read(CHUNK_SIZE)

  while True:
    if ffpmeg_process.poll() is not None:
      break
    time.sleep(1)

  exit_event.set()
  fifo_file_write_stream.close()
  fifo_file_mp4_stream.close()
  raw_video_input_stream.close()

  return;

logging.basicConfig(
  format="%(asctime)s: %(message)s",
  level=logging.INFO,
  datefmt="%H:%M:%S")

raw_video_stream = io.BytesIO()
mp4_video_stream = io.BytesIO()

logging.info("Creating threads")
feed_raw_video_thread = threading.Thread(target=feed_raw_video_stream, args=(raw_video_stream))
convert_mp4_thread = threading.Thread(target=convert_to_mp4,args=(raw_video_stream, mp4_video_stream))
exit_event = threading.Event()
write_mp4_thread = threading.Thread(target=write_mp4_to_file,args=(mp4_video_stream, exit_event))

logging.info("Starting threads")
feed_raw_video_thread.start()
convert_mp4_thread.start()

feed_raw_video_thread.join()
convert_mp4_thread.join()

exit_event.set()
write_mp4_thread.join()
