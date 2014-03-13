#!/usr/bin/env python

import os
from setuptools import find_packages
from distutils.core import setup

basepath = os.path.dirname(os.path.abspath(__file__))
packages = find_packages(basepath)

setup(
    name='lettuce_tools',
    version='0.1',
    author='rafaelh, pge354, arobres, sdmt',
    author_email='',
    url='',
    description='Lettuce Tools',
    packages=packages,
    entry_points={
        'console_scripts': ['lettuce_tools = lettuce_tools.lettuce_tools.lettuce_tools:main'],
        },
    install_requires=['colorama==0.2.5', 'argparse==1.2.1'])
