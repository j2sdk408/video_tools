"""adjust .srt scaler & offset
"""

import re
import sys


class SrtLine(object):
    """class for single line in .srt"""

    def __init__(self, idx):
        """initializer"""

        self.idx = idx
        self.time_st = ""
        self.time_ed = ""
        self.lines = []

    def get_time(self, offset=0, scale=1):
        """print adjusted time string
        offset: unit: ms, + means delay
        scale: shorten/stretch time
        """

        time_out = []

        for time in [self.time_st, self.time_ed]:
            m = re.search(r"([0-9]+):([0-9]+):([0-9]+),([0-9]+)", time)
            t_hr = int(m.group(1))
            t_min = int(m.group(2))
            t_sec = int(m.group(3))
            t_msec = int(m.group(4))
            total_m = (t_hr * 3600 + t_min * 60 + t_sec) * 1000 + t_msec

            # calculate new time
            total_m = total_m * scale + offset

            out_msec = total_m % 1000
            out_sec = (total_m / 1000) % 60
            out_min = ((total_m / 1000) % 3600) / 60
            out_hr = ((total_m / 1000) / 3600)
            time_out.append("%02d:%02d:%02d,%03d" % (out_hr, out_min, out_sec, out_msec))

        return time_out


class SrtInfo(object):
    """class for whole .srt file"""

    def __init__(self):
        """initializer"""

        self.srt_list = []
        self.offset = 0
        self.scale = 1

    def __str__(self):
        """to string"""

        out_list = []

        for srt in self.srt_list:
            out_list.append(str(srt.idx))

            # get calculated time
            curr_time = srt.get_time(
                self.offset,
                self.scale
            )

            out_list.append("%s --> %s" % (curr_time[0], curr_time[1]))
            out_list.append("\n".join(srt.lines))
            out_list.append("")

        out_list.append("")

        return "\n".join(out_list)

    def load(self, content_list):
        """parse .srt from content list"""

        self.srt_list = []
        state = 0
        line_cnt = 1

        for idx, line in enumerate(content_list):
            if state == 0 and line:
                try:
                    if int(line) == line_cnt:
                        self.srt_list.append(SrtLine(line_cnt))
                        line_cnt += 1
                        state = 1
                except:
                    break

            elif state == 1:
                m = re.search(r"(.*) --> (.*)", line)
                self.srt_list[-1].time_st = m.group(1)
                self.srt_list[-1].time_ed = m.group(2)
                state = 2

            else:
                if line:
                    self.srt_list[-1].lines.append(line)
                else:
                    state = 0


if __name__ == "__main__":

    #file_name = "Chicago_BDRip_1080p_CRUSADERS.srt"
    #file_name = "old.srt"
    file_name = sys.argv[1]

    with open(file_name, "r") as f:
        content = f.read().splitlines()

    sf = SrtInfo()
    sf.load(content)

    # 00:03:10,620 : old
    # 00:03:12,097 : standard
    t_st1 = (3) * 60 + 10.620
    t_st2 = (3) * 60 + 12.097

    # 01:48:54,600 : old
    # 01:48:56,268 : standard
    t_ed1 = 1 * 60 * 60 + 48 * 60 + 54.600
    t_ed2 = 1 * 60 * 60 + 48 * 60 + 56.268

    t1 = t_st1
    d1 = (t_st1 - t_st2) * 1000

    t2 = t_ed1
    d2 = (t_ed1 - t_ed2) * 1000

    sf.offset = -(d1 + (d1 - d2) / (t2 - t1) * t1)
    sf.scale = (1. - (d2 - d1) / (t2 - t1) / 1000)

    print str(sf)

