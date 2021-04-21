#!/usr/bin/env python3
# Copyright 2021 Tolteck

import ast
import pathlib

import setuptools

path = str(pathlib.Path(__file__).parent.absolute()) + '/couchcopy'
version = [n.value.s for n in ast.parse(open(path).read()).body
           if isinstance(n, ast.Assign)
           and n.targets[0].id == '__version__'][0]

setuptools.setup(
    name='couchcopy',
    version=version,
    author='Hoël Iris',
    url='https://github.com/tolteck/couchcopy',
    description='Backup, load and restore CouchDB clusters',
    long_description=open('README.rst').read(),
    license='GPLv3',
    scripts=['couchcopy'],
    install_requires=[
        'aiocouch >=1.1.0',
        'PyYAML >=3.11',
    ],
    python_requires='>=3.8',
)
