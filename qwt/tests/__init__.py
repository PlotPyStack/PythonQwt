# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt test package
======================
"""

def run():
    """Run PythonQwt test launcher (requires `guidata`)"""
    import qwt
    try:
        from guidata.guitest import run_testlauncher
    except ImportError:
        raise ImportError("This feature requires `guidata` 1.7+.")
    run_testlauncher(qwt)

if __name__ == '__main__':
    run()
    