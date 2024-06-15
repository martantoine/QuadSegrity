#!/bin/sh
ffmpeg -y -i walking.mp4 -vf "crop=818:420:30:0" output.mp4

ffmpeg -y -ss 0 -i output.mp4 -to 00:28.9 -c:v copy -c:a copy output1.mp4

ffmpeg -y -i output1.mp4 -vf "drawtext=fontfile=/usr/share/fonts/TTF/HackNerdFontMono.ttf:text='Goofy, Antoine Vincent Martin, speed x2\: %{pts\:hms}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=400" -codec:a copy output2.mp4
ffmpeg -y -i output2.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" walking-final.mp4
rm output.mp4 output1.mp4 output2.mp4
