"""merging .ts files

Steps:
1. create a .txt file with the following format:
    file '/path/to/file1'
    file '/path/to/file2'
    file '/path/to/file3'

2. run ffmpeg
    ffmpeg -f concat -i mylist.txt -c copy all.ts

3. convert to .mp4
    ffmpeg -i all.ts -acodec copy -vcodec copy all.mp4

reference:
https://superuser.com/questions/692990/use-ffmpeg-copy-codec-to-combine-ts-files-into-a-single-mp4
"""

import os
import subprocess


def gen_config(config_name):
    """generate config file for .ts video list
    """

    file_list = [
        x for x in os.listdir(".") if x.endswith(".ts")
    ]
    file_list = sorted(file_list)

    with open(config_name, "w") as f:
        for file_name in file_list:
            f.write(
                "file '%s'\n" % file_name
            )

def merge_ts(target_dir="."):
    """merge with ffmpeg

    Args:
        target_dir(str): target directory for search
    """

    os.chdir(target_dir)

    config_name = "config.txt"
    merged_file = "merged.ts"
    output_file = "out.mp4"

    print "Generationg config.txt"
    gen_config(config_name)

    print "Merging..."
    cmd = "ffmpeg -f concat -i %s -c copy %s" % (
        config_name,
        merged_file
    )
    subprocess.call(cmd, shell=True)

    print "Transcoding..."
    cmd = "ffmpeg -i %s -acodec copy -vcodec copy %s" % (
        merged_file,
        output_file
    )
    subprocess.call(cmd, shell=True)

    print "Done"


if __name__ == "__main__":
    merge_ts()

