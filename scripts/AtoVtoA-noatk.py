#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This script was created on the 5th of May 2021 at 8:12 PM. 
## The comments and help text have been replaced, but the code is verbatim, confusing naming conventions and all.
## This is the 4th iteration of the process. This uses a mu-law compander to increase the dynamic range of the 8-bit PCM. This is a fixed version of the round 3 script.
## Kept for historical purposes only. No updates will be accepted for this script.

import subprocess
import sys
import os

## This script assumes you have FFmpeg and SoX installed in PATH.
## If editing, you MUST encase all parameters in quotes, including the numbers.
## No error-correction done on variables; the whole script expects string type for most variables.
## You will need at least 2.5 times the size of the original audio file free on disk. Be warned!

## Prints usage information if given no parameters.
#print(sys.argv)
if len(sys.argv) == 1:
    print(f"Usage: {os.path.basename(__file__)} [sample rate] [no. of channels] [filename w/ extension] [video codec] [bitrate] [internal resolution] \n")
    sys.exit()

## Variables

#### Step 0
## Setting intermediate_format to anything other than "u8" will likely lead to severely-distorted audio. You have been warned!
intermediate_format = "u8"
sample_rate = sys.argv[1]

## Compander parameters.
x_dB = (-60,-50,-40,-30,-20,-10)
y_dB = (-28,-19,-13, -8, -5, -2)
compress_dB = ""
expand_dB = ""
gain_dB = "-12"

for i in range(0,len(x_dB)):
    if i == (len(x_dB) - 1):
        compress_dB +=f"{x_dB[i]}/{y_dB[i]}"
        expand_dB += f"{y_dB[i]}/{x_dB[i]}"
    else:
        compress_dB += f"{x_dB[i]}/{y_dB[i]}|"
        expand_dB += f"{y_dB[i]}/{x_dB[i]}|"




#### Step 1

in_filename = os.path.splitext(sys.argv[3])[0]
in_extension = os.path.splitext(sys.argv[3])[1]

step2_out_extension = ".mkv"
resolution = sys.argv[6]
framerate = "30"
pixel_format = "rgb24"
video_codec = sys.argv[4]
bitrate_codec = sys.argv[5]

#### Step 2
# (no new variables; all recycled from Step 1)

#### Step 3.
## File-specific parameters. Set these equal to the original video's settings.
channels = sys.argv[2]

## Final audio codec.
step4_out_extension = "flac"
out_audio_codec = "flac"
out_bit_depth = "24"

## Combined variables. Used for brevity.
compress = f"compand=points={compress_dB}:volume={gain_dB}"
expand =   f"compand=points={expand_dB}:volume=0"

in_file = f"{in_filename}{in_extension}"
step1_out = f"{in_filename}-step1-compressed"
step2_out = f"{in_filename}-step2-{video_codec}-{bitrate_codec}-{resolution}"
step3_out = f"{in_filename}-step3-{video_codec}-{bitrate_codec}-{resolution}"
step4_out = f"{in_filename}-end-{video_codec}-{bitrate_codec}-{resolution}"

## Step 1: Compresses (in the audio engineering sense, not the computing sense), then normalizes an input audio file.
## Saves it as 8-bit PCM. Compression here prevents the -48 dB noise floor inherent in 8-bit PCM from interfering with the output later.
step1_list = ["ffmpeg","-y","-i",in_file,
              "-af",compress,
              "-f",intermediate_format,
              "-r",sample_rate,
              f"{step1_out}.raw"]
print(step1_list)
subprocess.run(step1_list)

## Step 2: Encode the compressed 8-bit PCM in a video codec of your choice.
step2_list = ["ffmpeg","-y","-f","rawvideo","-s",resolution,"-r",framerate,"-pix_fmt",pixel_format,
              "-i",f"{step1_out}.raw","-c:v",video_codec,"-b:v",bitrate_codec,f"{step2_out}.{step2_out_extension}"]
print(step2_list)
subprocess.run(step2_list)


## Step 3: Decode the encoded "video" back into raw video.
step3_list = ["ffmpeg","-y","-i",f"{step2_out}.{step2_out_extension}","-f","rawvideo","-r",framerate,"-pix_fmt",pixel_format,f"{step3_out}.raw"]
print(step3_list)
subprocess.run(step3_list)

## Step 4: Use FFmpeg to interpret our raw video back into 8-bit PCM.
## Expands the audio, re-gains it, and spits out the same format as the input.
step4_list = ["ffmpeg","-y","-f",intermediate_format,"-ar",sample_rate,"-ac",channels,"-i",f"{step3_out}.raw",
              "-af",expand,"-c:a",out_audio_codec,"-ar",sample_rate,f"{step4_out}.{step4_out_extension}"]
print(step4_list)
subprocess.run(step4_list)