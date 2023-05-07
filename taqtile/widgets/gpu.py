# Copyright (c) 2022 Steven Joseph (jagguli)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile.widget import base
from collections import OrderedDict
import json
import subprocess
import sys
import time
import xml.etree.ElementTree


class GPU(base.ThreadPoolText):
    """
    A simple widget to display GPU load and frequency.

    """

    defaults = [
        ("update_interval", 1.0, "Update interval for the GPU widget"),
        (
            "format",
            "GPU {gpu_util}GHz {mem_used_per}%",
            "GPU display format",
        ),
    ]

    def __init__(self, **config):
        super().__init__("", **config)
        self.add_defaults(GPU.defaults)

    def poll(self):
        try:
            return self.format.format(**self.get_stats())
        except KeyError:
            return 'err'

    def get_stats(self):
        # based on https://github.com/alwynmathew/nvidia-smi-python/blob/master/gpu_stat.py
        def extract(elem, tag, drop_s):
            text = elem.find(tag).text
            if drop_s not in text:
                raise Exception(text)
            text = text.replace(drop_s, "")
            try:
                return int(text)
            except ValueError:
                return round(float(text), 2)

        i = 0

        d = OrderedDict()
        d["time"] = time.time()
        d["gpu_util"] = "na"
        d["msg"] = "GPU status: Unavail \n"
        d['mem_used_per'] = '0'

        cmd = ["nvidia-smi", "-q", "-x"]
        try:
            cmd_out = subprocess.check_output(cmd)
        except:
            return d
            
        gpu = xml.etree.ElementTree.fromstring(cmd_out).find("gpu")

        util = gpu.find("utilization")
        d["gpu_util"] = extract(util, "gpu_util", "%")

        d["mem_used"] = extract(gpu.find("fb_memory_usage"), "used", "MiB")
        d["mem_used_per"] = round(d["mem_used"] * 100 / 11171, 2)

        if d["gpu_util"] < 15 and d["mem_used"] < 2816:
            d["msg"] = "GPU status: Idle \n"
        else:
            d["msg"] = "GPU status: Busy \n"
        return d
