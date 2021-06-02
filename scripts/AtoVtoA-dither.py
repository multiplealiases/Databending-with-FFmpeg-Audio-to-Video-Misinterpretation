#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This script was created on the 7th of May 2021 at 10:26 PM. 
## The comments and help text have been replaced, but the code is verbatim, confusing naming conventions and all.
## This shows the detrimental effects of dither on u-law companding.
## Kept for historical purposes only. No updates will be accepted for this script, but you're free to fork it on your own under the terms of the MIT license.

import subprocess
import sys
import os

## This script assumes you have FFmpeg and SoX installed in PATH.
## If editing, you MUST encase all parameters in quotes, including the numbers.
## No error-correction done on variables; the whole script expects string type.
## You will need at least 2.5 times the size of the original video file free on disk. Be warned!
## Only accepts 8-bit PCM.


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
dB_list = [(-80.0,-46.86), (-79.02,-45.89), (-77.99,-44.88), (-77.02,-43.92), (-76.03,-42.95), (-75.04,-41.98),
 (-74.02,-40.99), (-73.0,-39.98), (-72.01,-39.02), (-71.0,-38.05), (-70.01,-37.09),
 (-69.0,-36.12), (-68.0,-35.17), (-67.01,-34.23), (-66.0,-33.28), (-65.01,-32.34),
 (-64.0,-31.4), (-63.0,-30.48), (-62.0,-29.56), (-61.0,-28.65), (-60.0,-27.75),
 (-59.0,-26.86), (-58.0,-25.98), (-57.0,-25.12), (-56.0,-24.26), (-55.0,-23.42),
 (-54.0,-22.6), (-53.0,-21.78), (-52.0,-20.98), (-51.0,-20.2), (-50.0,-19.44),
 (-49.0,-18.7), (-48.0,-17.97), (-47.0,-17.26), (-46.0,-16.57), (-45.0,-15.9),
 (-44.0,-15.24), (-43.0,-14.61), (-42.0,-14.0), (-41.0,-13.4), (-40.0,-12.82),
 (-39.0,-12.27), (-38.0,-11.72), (-37.0,-11.2), (-36.0,-10.7), (-35.0,-10.21),
 (-34.0,-9.74), (-33.0,-9.29), (-32.0,-8.85), (-31.0,-8.42), (-30.0,-8.01),
 (-29.0,-7.61), (-28.0,-7.23), (-27.0,-6.86), (-26.0,-6.5), (-25.0,-6.15),
 (-24.0,-5.82), (-23.0,-5.49), (-22.0,-5.17), (-21.0,-4.87), (-20.0,-4.57),
 (-19.0,-4.28), (-18.0,-4.0), (-17.0,-3.72), (-16.0,-3.46), (-15.0,-3.2),
 (-14.0,-2.95), (-13.0,-2.7), (-12.0,-2.46), (-11.0,-2.23), (-10.0,-2.01),
 (-9.0,-1.78), (-8.0,-1.57), (-7.0,-1.36), (-6.0,-1.15), (-5.0,-0.95),
 (-4.0,-0.75), (-3.0,-0.56), (-2.0,-0.37), (-1.0,-0.18), (0.0,0.0)]

x_dB = [x for x,y in dB_list]
y_dB = [y for x,y in dB_list]

compress_dB = ""
expand_dB = ""

for i in range(0,len(x_dB)):
    if i == (len(x_dB) - 1):
        compress_dB +=f"{x_dB[i]},{y_dB[i]}"
        expand_dB += f"{y_dB[i]},{x_dB[i]}"
    else:
        compress_dB += f"{x_dB[i]},{y_dB[i]},"
        expand_dB += f"{y_dB[i]},{x_dB[i]},"


attack = "0"
release = "0"

knee_dB = "0.2"
out_gain_dB = "-12"

gain_dB = "-0.1"
delay = "0"
#### Step 1
dither_type = "-S"

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
compress_start_end = f"{knee_dB}:{compress_dB}"
expand_atk_release = f"{attack},{release}"
expand_start_end = f"{knee_dB}:{expand_dB}"

in_file = f"{in_filename}{in_extension}"
step0_out = f"{in_filename}-step0-compressed"
step1_out = f"{in_filename}-step1-{video_codec}-{bitrate_codec}-{resolution}"
step2_out = f"{in_filename}-step2-{video_codec}-{bitrate_codec}-{resolution}"
step3_out = f"{in_filename}-dither-{video_codec}-{bitrate_codec}-{resolution}"

# sox BigBuckBunny-stereo.flac -b 8 -r 48000 -e signed-integer -V BBB-audio-NS-1-compand.raw  compand 0.3,0.8 6:−60,-10 −5 gain -n -1

## Step 0: Compresses (in the audio engineering sense, not the computing sense), then normalizes an input audio file.
## Saves it as 8-bit PCM. Compression here prevents the -48 dB noise floor inherent in 8-bit PCM from interfering with the output later. It dithers in the process.
step0_list = ["sox",in_file,"-r",sample_rate,"-e",encoding,"-V","-b",bit_depth,"-c",channels,step0_out + ".raw","compand",compress_atk_release,compress_start_end,out_gain_dB,"0",delay,"gain","-n",gain_dB,"dither",dither_type]
print(step0_list)
subprocess.run(step0_list)

## Step 1: Takes in the 8-bit PCM as RGB 24-bit video (by default), and encodes it into a format of your choice.
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
