#!/usr/bin/python
"""
Convert Kodak pixel pro 4k video into top-bottom VR & 360 video with audio
Note: external dependencies:
    - mplayer & mencoder
    - python PIL lib
    - spatial-media-2.0 (from https://github.com/google/spatial-media)
"""

import subprocess
from PIL import Image
import os
import sys

mplayer_dir = r"D:\local program\mplayer-svn-37324-2-x86_64"
mplayer_bin = r"{}\mplayer.exe".format(mplayer_dir)
mencoder_bin = r"{}\mencoder.exe".format(mplayer_dir)

def run_command(cmd):
    """run commend using subprocess"""
    try:
        print cmd
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as exc:
        print exc.output
        sys.exit(1)

input_file = sys.argv[1]
input_name = input_file.split(".")[0]
output_file = "vr_output"
output_dir = "output_%s" % input_name

print "Input: %s..." % input_file

print "Creating output folter %s..." % output_dir
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
os.chdir(output_dir)    

print "Converting to .png & .wav..."
run_command(r""""%s" ..\%s -vo png:z=6 -ao pcm""" % (mplayer_bin, input_file))

black = Image.open("../black.png")
#os.chdir("output")

print "Updating .png...",
for png_file in [x for x in os.listdir(".") if x.endswith("png")]:

    print ".",
    orig = Image.open(png_file)

    out = Image.new("RGB", (3840, 3840))
    out.paste(orig, (0, 0))
    out.paste(orig, (-1920, 1920))
    out.paste(orig, (1920, 1920))
    out.paste(black, (0, 0))
    out.paste(black, (960 + 1920, 0))
    out.paste(black, (0, 1920))
    out.paste(black, (960 + 1920, 1920))
    
    orig.close()
    out.save(png_file)
print "done."

print "Converting .png & .wav to .mp4..."
input_setting = "mf://*.png -mf fps=30"
ovc_setting = r"-ovc x264"
oac_setting = r"-oac mp3lame -audiofile audiodump.wav"
of_setting = r"-of lavf -lavfopts format=mp4"
run_command(r""""{}" {} {} {} {} -o ..\{}.mp4""".format(mencoder_bin, input_setting, ovc_setting, oac_setting, of_setting, output_file))


print "Injecting VR & 360 codec..."

os.chdir("../spatial-media-2.0")
run_command("python spatialmedia -s top-bottom -i ..\{0}.mp4 ..\{0}_codec.mp4".format(output_file))

print "done."
