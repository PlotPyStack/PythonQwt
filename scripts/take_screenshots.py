# Copyright (c) 2026 PlotPyStack developers
# Licensed under the terms of the MIT License
# (see LICENSE file for more details)

"""Screenshots update script."""

import subprocess
import sys


def main():
    """Run all screenshot-generating scripts."""
    scripts = [
        [sys.executable, "qwt/tests/__init__.py", "--mode", "screenshots"],
        [sys.executable, "doc/plot_example.py"],
        [sys.executable, "doc/symbol_path_example.py"],
    ]
    for cmd in scripts:
        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
