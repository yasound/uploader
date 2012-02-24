#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import uploader

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

required = ['mutagen',
            'psycopg2',
            'requests',]
packages = [
    'uploader',
]

setup(
    name='uploader',
    version=uploader.__version__,
    description='Uploader for Yasound.',
    long_description=open('README.markdown').read() + '\n\n' +
                     open('HISTORY.markdown').read(),
    author='Jérôme Blondon',
    author_email='jerome@yasound.com',
    url='https://github.com/yasound/uploader',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    include_package_data=True,
    install_requires=required,
    license='Proprietary',
    classifiers=(
    ),
)


