#!/usr/bin/env python3.6

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='led-matrix-driver',
    version='1.0',
    description='Control LED matrix',
    author='M. Barry McAndrews',
    author_email='bmcandrews@pitt.edu',
    ext_modules=cythonize(['data_sources.py', 'matrix.py']),
    requires=['Cython', 'uvloop', 'aiofiles', 'setproctitle', 'Pillow']
)
