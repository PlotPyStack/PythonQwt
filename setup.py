# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see qwt/LICENSE for details)

"""
qwt
====

Qt Widget Tools for Python
"""

from __future__ import print_function

import os
import sys
import os.path as osp

from distutils.core import setup
from distutils.command.build import build

LIBNAME = 'qwt'
from qwt import __version__ as version

DESCRIPTION = 'qwt is a pure Python implementation of Qwt C++ library, using PyQt and NumPy'
LONG_DESCRIPTION = ''
KEYWORDS = ''
CLASSIFIERS = ['Development Status :: 5 - Production/Stable',
               'Topic :: Scientific/Engineering']


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
      download_url='http://%s.googlecode.com/files/%s-%s.zip' % (
                                                  LIBNAME, LIBNAME, version),
      description=DESCRIPTION, long_description=LONG_DESCRIPTION,
      packages=get_subpackages(LIBNAME),
      package_data={LIBNAME:
                    get_package_data(LIBNAME, ('.png', '.svg', '.mo'))},
      requires=["PyQt4 (>4.3)",],
      author = "Pierre Raybaut",
      author_email = 'pierre.raybaut@gmail.com',
#      url = 'http://www.cea.fr',
      classifiers=CLASSIFIERS + [
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
