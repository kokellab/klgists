#!/usr/bin/env python3
# coding=utf-8

from distutils.core import setup

setup(
    name='klgists',
    version='0.0.1',
    description='A collection of Python snippets for the Kokel Lab',
    author='Douglas Myers-Turnbull',
    url='https://github.com/kokellab/klgists',
    packages=['klgists', 'klgists.analysis', 'klgists.bioinf', 'klscripts.common', 'klscripts.db', 'klscripts.files', 'klscripts.misc', 'klscripts.pandas', 'klscripts.plotting', 'tests'],
    package_dir='',
    test_suite='tests',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        'Intended Audience :: Science/Research',
        'Natural Language :: English'
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
