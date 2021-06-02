#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This script was created on the 17th of April 2021.
## The comments and help text have been replaced, but the code is verbatim, confusing naming conventions and all.
## This is the 2nd iteration of the process. This isn't very good.
## Kept for historical purposes only. No updates will be accepted for this script, but you're free to fork it on your own under the terms of the MIT license.

## This script assumes you have FFmpeg and SoX installed in PATH.
## If editing, you MUST encase all parameters in quotes, including the numbers.
## No error-correction done on variables; the whole script expects string type.
## You will need at least 2.5 times the size of the original audio file free on disk. Be warned!

import subprocess
import sys
import os


## Prints usage information if given no parameters.
#print(sys.argv)
if len(sys.argv) == 1:
    print("Usage: audio-autoencode-compander [sample rate] [no. of channels] [filename w/ extension] [video codec] [bitrate] [internal resolution] \n")
    sys.exit()

## Variables

#### Step 0
## Setting bit_depth to anything other than 8 will likely lead to severely-distorted audio. You have been warned!
bit_depth = "8"
sample_rate = sys.argv[1]
## Theoretically-changeable, but SoX will not allow signed 8-bit PCM as output.
encoding = "unsigned-integer"

## Compander parameters.
attack = "1"
release = "1"

knee_dB = "6"
start_dB = "-60"
end_dB = "-10"
out_gain_dB = "-9"

gain_dB = "-1"
delay = "0.01"
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
out_audio_codec = ".flac"
out_bit_depth = "24"

## Combined variables. Used for brevity.
compress_atk_release = f"{attack},{release}"
compress_start_end = f"{knee_dB}:{start_dB},{end_dB}"
expand_atk_release = f"{attack},{release}"
expand_start_end = f"{knee_dB}:{end_dB},{start_dB}"

in_file = f"{in_filename}{in_extension}"
step0_out = f"{in_filename}-step0-compressed"
step1_out = f"{in_filename}-step1-{video_codec}-{bitrate_codec}-{resolution}"
step2_out = f"{in_filename}-step2-{video_codec}-{bitrate_codec}-{resolution}"
step3_out = f"{in_filename}-{attack}-{release}-{delay}-{video_codec}-{bitrate_codec}-{resolution}"

## Step 0: Compresses (in the audio engineering sense, not the computing sense), then normalizes an input audio file.
## Saves it as 8-bit PCM. Compression here prevents the -48 dB noise floor inherent in 8-bit PCM from interfering with the output later.
step0_list = ["sox",in_file ,"--plot","gnuplot","-r",sample_rate,"-e",encoding,"-V","-b",bit_depth,"-c",channels,step0_out + ".raw","compand",compress_atk_release,compress_start_end,out_gain_dB,"0",delay,"gain","-n",gain_dB]
print(step0_list)
subprocess.run(step0_list)

## Step 1: Uses FFmpeg to encode the raw audio as if it were video, using a video codec of your choice.
step1_list = ["ffmpeg","-y","-f","rawvideo","-s",resolution,"-r",framerate,"-pix_fmt",pixel_format,"-i",step0_out + ".raw","-c:v",video_codec,"-b:v",bitrate_codec,step1_out + step1_out_extension]
print(step1_list)
subprocess.run(step1_list)


## Step 2: Decode the encoded "video" back into raw video.
step2_list = ["ffmpeg","-y","-i",step1_out + step1_out_extension,"-f","rawvideo","-r",framerate,"-pix_fmt",pixel_format,step2_out + ".raw"]
print(step2_list)
subprocess.run(step2_list)

## Step 3: Use SoX to interpret our raw video back into 8-bit PCM.
## Expands the audio, re-gains it, and spits out the same format as the input.
step3_list = ["sox","-r",sample_rate,"-e",encoding,"-V","-b",bit_depth,"-c",channels,step2_out + ".raw","-b",out_bit_depth,"-c",channels,step3_out + in_extension,"compand",expand_atk_release,expand_start_end,out_gain_dB,"0",delay,"gain","-n",gain_dB]
print(step3_list)
subprocess.run(step3_list)
