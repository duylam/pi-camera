# pi-meeting

Enable video calls in Pi


## Setup Pi

1. OS: Raspbian GNU/Linux 8 (jessie)
1. Pi model: Pi 3 Model B
1. Run `install-ffmpeg.sh`
1. Use Python 2.7.9

## Development

- If coding on another machine (laptop), use `rsync` to copy files to Pi:

```bash
for (( ; ; ))
do
  rsync -avz --exclude '.git*' . <username on pi>@<pi IP>:/path/
  sleep 2
done
```

## Other mis notes

1.a Convert video to raw h264 codec
ffmpeg -i Untitled.mov -an -vcodec h264 -f h264 outfile.h264

-an : disable audio
-r : framerate
-f: force format
-c: codec code name

1.b Convert h264 to mp4 in pipe

cat outfile.h264 | ffmpeg -i - -codec copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1 > ffmpeg.fifo
cat ffmpeg.fifo > out2.mp4

List ffmpeg
ffmpeg -codecs
ffmpeg -encoders
ffmpeg -decoders
ffmpeg -formats
ffmpeg -protocols

for (( ; ; ))
do
  rsync -avz --exclude '.git*' . pi@pi:/home/pi/pi-meeting/
  sleep 2
done
