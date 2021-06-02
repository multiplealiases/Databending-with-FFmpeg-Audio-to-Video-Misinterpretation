#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This script was created on the 3rd of May 2021 at 8:12 PM. 
## The comments and help text have been replaced, but the code is verbatim, confusing naming conventions and all.
## This is the 3rd iteration of the process. This uses a mu-law compander. This script is somewhat broken; go for the round 4 script instead.
## Kept for historical purposes only. No updates will be accepted for this script, but you're free to fork it on your own under the terms of the MIT license.

import subprocess
import sys
import os

## This script assumes you have FFmpeg and SoX installed in PATH.
## If editing, you MUST encase all parameters in quotes, including the numbers.
## No error-correction done on variables; the whole script expects string type.
## You will need at least 2.5 times the size of the original audio file free on disk. Be warned!

## Prints usage information if given no parameters.
#print(sys.argv)
if len(sys.argv) == 1:
    print("Usage: audio-autoencode-ulaw-compander [sample rate] [no. of channels] [filename w/ extension] [video codec] [bitrate] [internal resolution] \n")
    sys.exit()

## Variables

#### Step 0
## Setting bit_depth to anything other than 8 will likely lead to severely-distorted audio. You have been warned!
intermediate_format = "u8"
sample_rate = sys.argv[1]

## Compander parameters.
attack = "0.1"
release = "0.1"
knee_dB = "1"
x_dB = (-80,-60,-50,-40,-30,-20,-10)
y_dB = (-47,-28,-19,-13, -8, -5, -2)
compress_dB = ""
expand_dB = ""

for i in range(0,len(x_dB)):
    if i == (len(x_dB) - 1):
        compress_dB +=f"{x_dB[i]}/{y_dB[i]}"
        expand_dB += f"{y_dB[i]}/{x_dB[i]}"
    else:
        compress_dB += f"{x_dB[i]}/{y_dB[i]}|"
        expand_dB += f"{y_dB[i]}/{x_dB[i]}|"


gain_dB = "-1"
delay = "0"
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
## File-specific parameters. Set these equal to the original video's settings.
channels = sys.argv[2]

## Final audio codec.
step3_out_extension = "flac"
out_audio_codec = "flac"
out_bit_depth = "24"

## Combined variables. Used for brevity.
attack_release = f"{attack}|{release}"

## Format is attack|release:{list of points}:in_gain:knee_dB:volume:delay
compress = f"compand={attack_release}:{attack_release}:{compress_dB}:{knee_dB}:-10:0:{delay}"
expand =   f"compand={attack_release}:{attack_release}:{expand_dB}:{knee_dB}:20:0:{delay}"

in_file = f"{in_filename}{in_extension}"
step0_out = f"{in_filename}-step0-compressed"
step1_out = f"{in_filename}-step1-{video_codec}-{bitrate_codec}-{resolution}"
step2_out = f"{in_filename}-step2-{video_codec}-{bitrate_codec}-{resolution}"
step3_out = f"{in_filename}-end-{video_codec}-{bitrate_codec}-{resolution}"

## Step 0: Compresses (in the audio engineering sense, not the computing sense), then normalizes an input audio file.
## Saves it as 8-bit PCM. Compression here prevents the -48 dB noise floor inherent in 8-bit PCM from interfering with the output later.
step0_list = ["ffmpeg","-y","-i",in_file,
              "-af",compress,
              "-f",intermediate_format,
              "-r",sample_rate,
              f"{step0_out}.raw"]
print(step0_list)
subprocess.run(step0_list)

## Step 1:
step1_list = ["ffmpeg","-y","-f","rawvideo","-s",resolution,"-r",framerate,"-pix_fmt",pixel_format,
              "-i",step0_out + ".raw","-c:v",video_codec,"-b:v",bitrate_codec,step1_out + step1_out_extension]
print(step1_list)
subprocess.run(step1_list)


## Step 2: Decode the encoded "video" back into raw video.
step2_list = ["ffmpeg","-y","-i",step1_out + step1_out_extension,"-f","rawvideo","-r",framerate,"-pix_fmt",pixel_format,f"{step2_out}.raw"]
print(step2_list)
subprocess.run(step2_list)

## Step 3: Use FFmpeg to interpret our raw video back into 8-bit PCM.
## Expands the audio, re-gains it, and spits out the same format as the input.
step3_list = ["ffmpeg","-y","-f",intermediate_format,"-ar",sample_rate,"-ac",channels,"-i",f"{step2_out}.raw",
              "-af",expand,"-c:a",out_audio_codec,"-ar",sample_rate,f"{step3_out}.{step3_out_extension}"]
print(step3_list)
subprocess.run(step3_list)