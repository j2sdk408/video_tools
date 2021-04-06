"""dump audio format
mplayer -ao pcm -af format=s16le -vo null input.mp4
"""

import wave
import numpy
from scipy import signal


def get_raw(wav_name):
    """get raw data from wave file
    Args:
        wav_name(str): wave file
    """

    f_wav = wave.open(wav_name, "rb")

    print("file: %s" % wav_name)
    print("audio info: %s" % str(f_wav.getparams()))

    # assign channels
    ch_list = []
    for _ in range(f_wav.getnchannels()):
        ch_list.append([])

    # get samples
    sample = f_wav.getsampwidth()
    assert sample in [1, 2]

    if sample == 1:
        value_fn = ord
    else:
        def value_fn(x):
            value = ord(x[0]) + ord(x[1]) * 256
            if value > 32767:
                value -= 0x10000
            return value

    while True:
        raw = f_wav.readframes(1)

        if not raw:
            break

        for idx, curr_ch in enumerate(ch_list):
            curr_ch.append(value_fn(raw[idx * sample:(idx + 1) * sample]))

    f_wav.close()

    return ch_list


def main():
    """main flow
    """
    wav_list = [
        "left\\audiodump.wav",
        "right\\audiodump.wav",
    ]

    list_l = get_raw(wav_list[0])[0]
    list_r = get_raw(wav_list[1])[0]
    #list_r = get_raw(wav_list[0])[1]

    window_len = 48000
    corr_list = []

    for idx in range(len(list_l) / window_len):
        array_l = numpy.array(list_l[idx * window_len: (idx + 1) * window_len])
        array_r = numpy.array(list_r[idx * window_len: (idx + 1) * window_len])
        corr = numpy.argmax(signal.correlate(array_l, array_r))
        print("#{}: {}".format(idx, corr))
        corr_list.append(corr)

    print("mean = {}".format(sum(corr_list) / len(corr_list)))

    with open("log.txt", "w") as f:
        f.write(str(corr_list))

if __name__ == "__main__":
    main()
