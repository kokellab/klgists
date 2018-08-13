#!/usr/bin/env python3
# coding=utf-8

from distutils.core import setup

setup(
	name='klgists',
	version='0.0.30',
	description='A collection of Python snippets for the Kokel Lab',
	author='Douglas Myers-Turnbull',
	url='https://github.com/kokellab/klgists',
	packages=['klgists', 'klgists.analysis', 'klgists.bioinf', 'klgists.common', 'klgists.db', 'klgists.files', 'klgists.misc', 'klgists.pandas', 'klgists.plotting', 'tests'],
	package_dir='',
	test_suite='tests',
	classifiers=[
		"Development Status :: 3 - Alpha",
		'Intended Audience :: Science/Research',
		'Natural Language :: English'
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	],
)
