# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 22:35:06 2014

@author: eegroopm
setup file for Cython extensions
"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("dspace", ["_dspace.pyx"],include_dirs=[numpy.get_include()])]
)
