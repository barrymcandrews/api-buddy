#!/usr/bin/env python3.6

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='led-matrix',
    version='1.5',
    description='Control LED matrix',
    author='M. Barry McAndrews',
    author_email='bmcandrews@pitt.edu',
    ext_modules=cythonize([]),
    requires=['Cython', 'uvloop', 'aiofiles', 'setproctitle', 'Pillow', 'hbmqtt']
)
