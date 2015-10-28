# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PyQwt5 vs. PythonQwt
====================
"""

import os
import os.path as osp
import sys
import subprocess
import time


def run_script(filename, args=None, wait=True):
    """Run Python script"""
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
    
    command = [sys.executable, '"'+filename+'"']
    if args is not None:
        command.append(args)
    proc = subprocess.Popen(" ".join(command), shell=True)
    if wait:
        proc.wait()


def main():
    for name in ('CurveBenchmark.py', 'CurveStyles.py',):
        for args in (None, 'only_lines'):
            for value in ('', '1'):
                os.environ['USE_PYQWT5'] = value
                filename = osp.join(osp.dirname(osp.abspath(__file__)), name)
                run_script(filename, wait=False, args=args)
                time.sleep(4)


if __name__ == '__main__':
    main()
    