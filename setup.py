#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name='LandBOSSE',
    version='0.1.0',
    description='Land-based Balance-of-System Systems Engineering Model',
    author='A. Eberle',
    author_email='annika.eberle@nrel.gov',
    install_requires=['pandas', 'numpy', 'seaborn', 'scipy', 'shapely', 'sympy'],
    packages=['landbosse'],
    license='Apache License, Version 2.0',
    dependency_links=['https://github.com/WISDEM/LandBOSSE'],
    zip_safe=False
)
