# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt
=========

Qt plotting widgets for Python
"""

from __future__ import print_function

import os
import sys
import os.path as osp
import subprocess
import shutil
import atexit

import setuptools  # analysis:ignore
from distutils.core import setup

LIBNAME = 'PythonQwt'
PACKAGE_NAME = 'qwt'
from qwt import __version__ as version

DESCRIPTION = 'Qt plotting widgets for Python'
LONG_DESCRIPTION = """\
PythonQwt: Qt plotting widgets for Python
=========================================

.. image:: http://pythonhosted.org/PythonQwt/_images/panorama.png

The ``PythonQwt`` package is a 2D-data plotting library using Qt graphical 
user interfaces for the Python programming language. It is compatible with 
both ``PyQt4`` and ``PyQt5`` (``PySide`` is currently not supported but it
could be in the near future as it would "only" requires testing to support 
it as a stable alternative to PyQt).

The ``PythonQwt`` project was initiated to solve -at least temporarily- the 
obsolescence issue of `PyQwt` (the Python-Qwt C++ bindings library) which is 
no longer maintained. The idea was to translate the original Qwt C++ code to 
Python and then to optimize some parts of the code by writing new modules 
based on NumPy and other libraries.

The ``PythonQwt`` package consists of a single Python package named `qwt` 
which is a pure Python implementation of Qwt C++ library with some 
limitations: efforts were concentrated on basic plotting features, leaving 
higher level features to the `guiqwt` library.

See `README`_ and `documentation`_ for more details on the library and `changelog`_ for recent history of changes.

.. _README: https://github.com/PierreRaybaut/PythonQwt/blob/master/README.md
.. _documentation: http://pythonhosted.org/PythonQwt/
.. _changelog: https://github.com/PierreRaybaut/PythonQwt/blob/master/CHANGELOG.md
"""
KEYWORDS = ''
CLASSIFIERS = []
if 'beta' in version or 'b' in version:
    CLASSIFIERS += ['Development Status :: 4 - Beta']
elif 'alpha' in version or 'a' in version or version.startswith('0.'):
    CLASSIFIERS += ['Development Status :: 3 - Alpha']
else:
    CLASSIFIERS += ['Development Status :: 5 - Production/Stable']


def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name)+len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith('.') and osp.splitext(fname)[1] in extlist:
                flist.append(osp.join(dirpath, fname)[offset:])
    return flist

def get_subpackages(name):
    """Return subpackages of package *name*"""
    splist = []
    for dirpath, _dirnames, _filenames in os.walk(name):
        if osp.isfile(osp.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))
    return splist

def build_chm_doc(libname):
    """Return CHM documentation file (on Windows only), which is copied under 
    {PythonInstallDir}\Doc, hence allowing Spyder to add an entry for opening 
    package documentation in "Help" menu. This has no effect on a source 
    distribution."""
    args = ''.join(sys.argv)
    if os.name == 'nt' and ('bdist' in args or 'build' in args):
        try:
            import sphinx  # analysis:ignore
        except ImportError:
            print('Warning: `sphinx` is required to build documentation',
                  file=sys.stderr)
            return
        hhc_base = r'C:\Program Files%s\HTML Help Workshop\hhc.exe'
        for hhc_exe in (hhc_base % '', hhc_base % ' (x86)'):
            if osp.isfile(hhc_exe):
                break
        else:
            print('Warning: `HTML Help Workshop` is required to build CHM '\
                  'documentation file', file=sys.stderr)
            return
        doctmp_dir = 'doctmp'
        subprocess.call('sphinx-build -b htmlhelp doc %s' % doctmp_dir,
                        shell=True)
        atexit.register(shutil.rmtree, osp.abspath(doctmp_dir))
        fname = osp.abspath(osp.join(doctmp_dir, '%s.chm' % libname))
        subprocess.call('"%s" %s' % (hhc_exe, fname), shell=True)
        if osp.isfile(fname):
            return fname
        else:
            print('Warning: CHM building process failed', file=sys.stderr)

CHM_DOC = build_chm_doc(LIBNAME)


setup(name=LIBNAME, version=version,
      description=DESCRIPTION, long_description=LONG_DESCRIPTION,
      packages=get_subpackages(PACKAGE_NAME),
      package_data={PACKAGE_NAME:
                    get_package_data(PACKAGE_NAME, ('.png', '.svg', '.mo'))},
      data_files=[(r'Doc', [CHM_DOC])] if CHM_DOC else [],
      install_requires=["NumPy>=1.3"],
      extras_require = {
                        'Doc':  ["Sphinx>=1.1"],
                        'Tests':  ["guidata>=1.7.0"],
                        },
      entry_points={'gui_scripts':
                    ['PythonQwt-tests-py%d = qwt.tests:run [Tests]'\
                     % sys.version_info.major,]},
      author = "Pierre Raybaut",
      author_email = 'pierre.raybaut@gmail.com',
      url = 'https://github.com/PierreRaybaut/%s' % LIBNAME,
      platforms = 'Any',
      classifiers=CLASSIFIERS + [
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Widget Sets',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
      )
