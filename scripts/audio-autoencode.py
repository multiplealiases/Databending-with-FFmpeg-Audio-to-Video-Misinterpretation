#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This script was created on the 14th of April 2021 at 8:34 PM. 
## The comments and help text have been replaced, but the code is verbatim, confusing naming conventions and all.
## This is the 1st iteration of the process. This is the most direct approach possible, and it's awful.
## Kept for historical purposes only. No updates will be accepted for this script.

## This script assumes you have FFmpeg installed in PATH. If editing, you MUST encase all parameters in quotes, including the numbers.
## No error-correction done on variables; the whole script expects string type.
## You will need at least 2.5 times the size of the original audio file free on disk. Be warned!
## Only accepts raw 8-bit PCM.

import subprocess
import sys
import os

## Prints usage information if given no parameters.
print(sys.argv)
if len(sys.argv) == 1:
    print("Usage: audio-autoencode [sample rate] [no. of channels] [filename w/ extension] [video codec] [bitrate] [internal resolution] \nPlease encode your audio as raw 8-bit unsigned PCM first! The screams of the damned will emerge if you don't!")
    sys.exit()

## Variables

#### Step 1

in_filename = os.path.splitext(sys.argv[3])[0]
in_extension = os.path.splitext(sys.argv[3])[1]

step1_out_extension = ".mkv"
resolution = sys.argv[6]
framerate = "30"
pixel_format = "rgb24"
video_codec = sys.argv[4]
bitrate_codec = sys.argv[5]

#### Step 2
# (no new variables; all recycled from Step 1)

#### Step 3.
## File-specific parameters. Set these equal to the original audio's settings.
sample_rate = sys.argv[1]
channels = sys.argv[2]

## Final audio encoder.
out_audio_codec = "flac"
step3_format = "u8"

## Combined filenames. Used for brevity.
in_file = str(in_filename + in_extension)
step1_out = in_filename + "-" + video_codec + "-" + bitrate_codec + "-" + resolution
step2_out = in_filename + "-conv-" + video_codec + "-" + bitrate_codec + "-" + resolution
step3_out = in_filename + "-" + out_audio_codec + "-" + video_codec + "-" + bitrate_codec+ "-" + resolution

## Step 1: Interprets raw 8-bit PCM audio as raw 24-bit RGB video (by default; check "pix_fmt").
step1_list = ["ffmpeg","-y","-f","rawvideo","-s",resolution,"-r",framerate,"-pix_fmt",pixel_format,"-i",in_file,"-c:v",video_codec,"-b:v",bitrate_codec,step1_out+step1_out_extension]
print(step1_list)
subprocess.run(step1_list)

## Step 2: Decode the encoded "video" back into raw 8-bit PCM.
step2_list = ["ffmpeg","-y","-i",step1_out+step1_out_extension,"-f","rawvideo","-r",framerate,"-pix_fmt",pixel_format,step2_out+in_extension]
print(step2_list)
subprocess.run(step2_list)

## Step 3: Push our new raw audio into an audio codec, encoding to FLAC by default.
step3_list = ["ffmpeg","-y","-f", step3_format,"-ar",sample_rate,"-ac",channels,"-i",step2_out+in_extension,"-c:a",out_audio_codec,step3_out+".mkv"]
print(step3_list)
subprocess.run(step3_list)

