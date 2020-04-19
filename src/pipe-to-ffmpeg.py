import io
import os
import subprocess

print('start')

r_fd, w_fd = os.pipe()
r2_fd, w2_fd = os.pipe()

ffpmeg_process=subprocess.Popen([
  'ffmpeg', '-i', 'pipe:0', # todo: need to create pipe file in runtime
  '-codec copy',
  '-movflags frag_keyframe+empty_moov', # todo: temp fix for using .mov file only
  '-f mp4 pipe:1'
], stdin=r_fd, stdout=w2_fd)

print('done')

# 1. open file
# 3. spawn new ffpmeg to read from pipe file, convert to mp4
# 4. feed file to pipe file
# 5. get output from pipe file and save into file
# 6. save all into file
# 7. play on browser

# TODO: create .fifo file

print('hi')
