#!/usr/bin/env python

import os
from setuptools import find_packages
from distutils.core import setup

basepath = os.path.dirname(os.path.abspath(__file__))
packages = find_packages(basepath)

setup(
    name='tdaf_lettuce_tools',
    version='0.0.6-alpha',
    author='rafaelh, pge354',
    author_email='rafaelh@pdi.es, pge@grupoinnovati.com',
    url='',
    description='TDAF Lettuce Tools',
    packages=packages,
    entry_points={
        'console_scripts': ['lettucetdaf = tdaf_testcomponents.run_script.lettucetdaf:main'],
        },
    install_requires=['colorama==0.2.5', 'argparse==1.2.1'])
