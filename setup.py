# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
python-qwt
==========

Qt plotting widgets for Python
"""

from __future__ import print_function

import os
import sys
import os.path as osp

import setuptools  # analysis:ignore
from distutils.core import setup
from distutils.command.build import build

LIBNAME = 'python-qwt'
PACKAGE_NAME = 'qwt'
from qwt import __version__ as version

DESCRIPTION = 'Qt plotting widgets for Python'
LONG_DESCRIPTION = """\
The ``python-qwt`` project is a pure Python translation of the Qwt C++ library 
which implements Qt widgets for plotting curves. 
It consists of a single Python package named `qwt` (and examples, doc, ...).

The ``python-qwt`` project was initiated to solve -at least temporarily- the 
obsolescence issue of `PyQwt` (the Python-Qwt C++ bindings library) which is 
no longer maintained. The idea was to translate the Qwt C++ code to Python and 
then to optimize some parts of the code by writing new modules based on NumPy 
and other libraries.

The following ``Qwt`` classes won't be reimplemented in ``python-qwt`` because 
most powerful features already exist in ``guiqwt``: QwtCounter, QwtPicker, 
QwtPlotPicker, QwtPlotZoomer and QwtEventPattern.
QwtClipper is not implemented (and it will probably be very difficult or 
impossible to implement it in pure Python without performance issues). As a 
consequence, when zooming in a plot curve, the entire curve is still painted 
(in other words, when working with large amount of data, there is no 
performance gain when zooming in)."""
KEYWORDS = ''
CLASSIFIERS = []
if 'beta' in version or 'b' in version:
    CLASSIFIERS += ['Development Status :: 4 - Beta']
elif 'alpha' in version or 'a' in version:
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


try:
    import sphinx
except ImportError:
    sphinx = None
    
from distutils.command.build import build as dftbuild

class build(dftbuild):
    def has_doc(self):
        if sphinx is None:
            return False
        setup_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.isdir(os.path.join(setup_dir, 'doc'))
    sub_commands = dftbuild.sub_commands + [('build_doc', has_doc)]

cmdclass = {'build' : build}

if sphinx:
    from sphinx.setup_command import BuildDoc
    class build_doc(BuildDoc):
        def run(self):
            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version
            build = self.get_finalized_command('build')
            sys.path.insert(0, os.path.abspath(build.build_lib))
            try:
                sphinx.setup_command.BuildDoc.run(self)
            except UnicodeDecodeError:
                print("ERROR: unable to build documentation because Sphinx do not handle source path with non-ASCII characters. Please try to move the source package to another location (path with *only* ASCII characters).", file=sys.stderr)
            sys.path.pop(0)

    cmdclass['build_doc'] = build_doc


setup(name=LIBNAME, version=version,
      description=DESCRIPTION, long_description=LONG_DESCRIPTION,
      packages=get_subpackages(PACKAGE_NAME),
      package_data={PACKAGE_NAME:
                    get_package_data(PACKAGE_NAME, ('.png', '.svg', '.mo'))},
      requires=["PyQt4 (>4.3)",],
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
      cmdclass=cmdclass)
