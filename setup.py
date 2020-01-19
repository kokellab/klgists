#!/usr/bin/env python3
# coding=utf-8

from distutils.core import setup

setup(
	name='dscience_gists',
	version='0.9.0',
	description='A collection of Python snippets for the Kokel Lab',
	author='Douglas Myers-Turnbull',
	url='https://github.com/kokellab/klgists',
	packages=['dscience_gists', 'dscience_gists.analysis',  'dscience_gists.core', 'dscience_gists.tools', 'dscience_gists.support', 'tests'],
	package_dir='',
	test_suite='tests',
	classifiers=[
		"Development Status :: 3 - Alpha",
		'Intended Audience :: Science/Research',
		'Natural Language :: English'
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.7',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	],
)
