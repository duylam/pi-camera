import logging
import threading
import io
import os
import subprocess
import time

# Code gia, k sai khi co camera that
def feed_raw_video_stream(output_stream, stop_flag):
  FILE_READ_CHUNK_SIZE=1024
  FILE_BUFFER_SIZE=FILE_READ_CHUNK_SIZE*3
  file_read_stream = io.open('./outfile.h264', mode='rb', buffering=FILE_BUFFER_SIZE)

  bytes = file_read_stream.read(FILE_READ_CHUNK_SIZE)
  while bytes:
    if stop_flag.is_set(): break

    output_stream.write(bytes)
    bytes = file_read_stream.read(FILE_READ_CHUNK_SIZE)

  file_read_stream.close()
  return;

# code gia, code thiet la ghi ra mang
def write_mp4_to_file(input_stream, input_steam_end_flag, stop_flag):
  FILE_BUFFER_SIZE=1024
  file_write_stream = io.open('./final.mp4', mode='wb', buffering=FILE_BUFFER_SIZE)

  bytes = input_stream.read(FILE_BUFFER_SIZE)
  if stop_flag.is_set():
    return;

  while True:
    if stop_flag.is_set(): break

    if bytes:
      file_write_stream.write(bytes)
    else:
      if input_steam_end_flag.is_set(): break
      time.sleep(1)

    bytes = input_stream.read(FILE_BUFFER_SIZE)

  file_write_stream.close()
  return;

def convert_to_mp4(raw_video_input_stream, mp4_output_stream, stop_flag):
  CHUNK_SIZE=1024

  def forward_stream(source_stream, dst_stream, source_stream_end_flag):
    bytes = source_stream.read(CHUNK_SIZE)

    while True:
      print("forward_stream: %s", stop_flag.is_set())
      if stop_flag.is_set(): break

      if bytes:
        dst_stream.write(bytes)
      else:
        if source_stream_end_flag.is_set(): break
        time.sleep(1)

      bytes = source_stream.read(CHUNK_SIZE)

  print('starting')

  # try:
  #   print('starting2')
  #   fifo_file_write_stream = io.open('ffmpeg-in.fifo', mode='ab', buffering=CHUNK_SIZE)

  #   print('starting3')

  #   fifo_file_mp4_stream = io.open('ffmpeg-out.fifo', mode='rb', buffering=CHUNK_SIZE)
  # except:
  #   print("Oops!",sys.exc_info()[0],"occured.")

  print('created streams')

  ffmpeg_stdin_r_fd, ffmpeg_stdin_w_fd = os.pipe()
  ffmpeg_stdout_r_fd, ffmpeg_stdout_w_fd = os.pipe()
  ffmpeg_stdin_w_fd_stream = io.open(ffmpeg_stdin_w_fd, mode='wb', buffering=CHUNK_SIZE)
  ffmpeg_stdout_r_fd_stream = io.open(ffmpeg_stdout_r_fd, mode='rb', buffering=CHUNK_SIZE)
  ffpmeg_process=subprocess.Popen([
    'ffmpeg', '-i', '-','-codec', 'copy',
    '-movflags', 'frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
    '-f','mp4','pipe:1'
  ], stdin=ffmpeg_stdin_r_fd, stdout=ffmpeg_stdout_w_fd)

  exit_event = threading.Event()
  forward_stream_thread = threading.Thread(target=forward_stream, args=(ffmpeg_stdout_r_fd_stream, mp4_output_stream, exit_event))

  print('starting thread')

  forward_stream_thread.start()

  bytes = raw_video_input_stream.read(CHUNK_SIZE)
  while bytes:
    print("fifo_file_write_stream: %s", stop_flag.is_set())

    if stop_flag.is_set(): break

    ffmpeg_stdin_w_fd_stream.write(bytes)
    bytes = raw_video_input_stream.read(CHUNK_SIZE)

  while True:
    print("ffpmeg_process: %s", stop_flag.is_set())

    if stop_flag.is_set(): break
    if ffpmeg_process.poll() is not None: break
    time.sleep(1)

  exit_event.set()
  ffmpeg_stdin_w_fd_stream.close()
  ffmpeg_stdout_r_fd_stream.close()

  while True:
    if not forward_stream_thread.is_alive(): break
    time.sleep(1)

  if stop_flag.is_set():
    ffpmeg_process.kill()

  return;

logging.basicConfig(
  format="%(asctime)s: %(message)s",
  level=logging.INFO,
  datefmt="%H:%M:%S")

raw_video_stream = io.BytesIO()
mp4_video_stream = io.BytesIO()

stop_flag = threading.Event()

logging.info("Creating threads")
feed_raw_video_thread = threading.Thread(target=feed_raw_video_stream, args=(raw_video_stream, stop_flag,))
convert_mp4_thread = threading.Thread(target=convert_to_mp4,args=(raw_video_stream, mp4_video_stream, stop_flag,))
exit_event = threading.Event()
write_mp4_thread = threading.Thread(target=write_mp4_to_file,args=(mp4_video_stream, exit_event, stop_flag,))

try:
  logging.info("Starting threads")
  feed_raw_video_thread.daemon = True
  feed_raw_video_thread.start()
  convert_mp4_thread.daemon = True
  convert_mp4_thread.start()
  # write_mp4_thread.daemon = True
  # write_mp4_thread.start()

  # dummy code, k su dung khi co stream tu picamera
  while True:
    time.sleep(1)
    if not feed_raw_video_thread.is_alive(): break

  # thuc te k can doi vi stream co lien tuc
  while True:
    time.sleep(1)
    if not convert_mp4_thread.is_alive(): break

  # while True:
  #   time.sleep(1)
  #   if write_mp4_thread.is_alive(): break

except KeyboardInterrupt:
  print 'a'
  stop_flag.set()
  feed_raw_video_thread.join()
  convert_mp4_thread.join()
  # write_mp4_thread.join()
