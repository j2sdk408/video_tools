"""adjust .srt scaler & offset
"""

# pylint: disable=invalid-name

import re
import sys


class SrtLine(object):
    """class for single line in .srt"""

    def __init__(self, idx):
        """initializer"""

        self.idx = idx
        # int: number of line

        self.time_st = ""
        # str: start time string

        self.time_ed = ""
        # str: end time string

        self.lines = []
        # list of str: subtitle strings

    def get_time(self, offset=0, scale=1):
        """print adjusted time string
        Args:
            offset(float): unit: ms, + means delay
            scale(float): shorten/stretch time
        Returns:
            str: adjusted, formatted time string representation
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
        # list of SrtInfo: subtitle items

        self.offset = 0
        # float: offset to be applied
        #   - 0 means no delay

        self.scale = 1
        # float: scaler to be applied
        #   - 1 means no scale

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

    @classmethod
    def load_file(cls, srt_path):
        """load srt file
        Args:
            srt_path(str)
        Returns:
            cls:
        """

        with open(srt_path, "r") as f:
            content = f.read().splitlines()

        sf = SrtInfo()
        sf.load(content)

        return sf

    def load(self, content_list):
        """parse .srt from content list
        Args:
            content_list(list of str): content
        """

        self.srt_list = []
        state = 0
        line_cnt = 1

        for line in content_list:
            if state == 0 and line:
                try:
                    if int(line) == line_cnt:
                        self.srt_list.append(SrtLine(line_cnt))
                        line_cnt += 1
                        state = 1
                except ValueError:
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

    @staticmethod
    def str2sec(time_str):
        """convert time str into seconds
        Args:
            time_str(str):
            - format: 00:01:38,832
        Returns:
            float: seconds
        """

        total_sec = 0

        hour_str, min_str, sec_str = time_str.split(":")

        sec_str = sec_str.replace(",", "")

        total_sec = int(hour_str) *  3600 + int(min_str) * 60 + float(sec_str) / 1000

        return total_sec

    def correct(self, time_old, time_correct):
        """adjust offset and scale to correct time
        Args:
            time_old(tuple of str)
                - (time start, time end)
            time_correct(tuple of str)
                - (time start, time end)
        """

        st_old, ed_old = time_old
        st_new, ed_new = time_correct
        # str
        #   - format: 00:01:38,832

        t_st1 = self.str2sec(st_old)
        t_st2 = self.str2sec(st_new)
        t_ed1 = self.str2sec(ed_old)
        t_ed2 = self.str2sec(ed_new)

        t1 = t_st1
        d1 = (t_st1 - t_st2) * 1000

        t2 = t_ed1
        d2 = (t_ed1 - t_ed2) * 1000

        self.offset = -(d1 + (d1 - d2) / (t2 - t1) * t1)
        self.scale = (1. - (d2 - d1) / (t2 - t1) / 1000)

    @classmethod
    def merge(cls, srt_list, allow_duplicate=True):
        """merge srt files
        Args:
            srt_list(list of cls):
            allow_duplicate(bool): True to allow duplicate lines
        Returns:
            cls: merged cls
        """

        assert len(srt_list) >= 2

        new_srt = cls()
        base_srt = srt_list[0]

        search_base_list = [0] * len(srt_list)
        # list of int: previously searched item

        for item in base_srt.srt_list:

            for srt_idx in xrange(1, len(srt_list)):
                insert_srt = srt_list[srt_idx]

                line_idx = search_base_list[srt_idx]

                while line_idx < len(insert_srt.srt_list):

                    insert_item = insert_srt.srt_list[line_idx]

                    # check for overlap
                    if insert_item.time_ed <= item.time_st:
                        line_idx += 1
                        continue
                    if insert_item.time_st >= item.time_ed:
                        break

                    # append lines
                    item.lines += insert_item.lines
                    line_idx += 1

                if not allow_duplicate:
                    search_base_list[srt_idx] = line_idx

            new_srt.srt_list.append(item)

        return new_srt

def merge_srt():
    """merge srt
    """

    base_name = "en.srt"
    insert_name = "zh3.srt"

    srt_list = [
        SrtInfo.load_file(base_name),
        SrtInfo.load_file(insert_name),
    ]

    sf_new = SrtInfo.merge(
        srt_list,
        allow_duplicate=False,
    )

    print str(sf_new)

def main():
    """main flow
    """

    #file_name = "old.srt"
    file_name = sys.argv[1]

    sf = SrtInfo.load_file(file_name)

    sf.correct(
        ("00:03:10,620", "01:48:54,600"), # old
        ("00:03:12,097", "01:48:56,268"), # correct
    )

    print str(sf)

if __name__ == "__main__":
    main()
