#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""PathExt
    Built-in Path with super powers.
 - File: pathext/setup.py
 - Author: Havocesp <https://github.com/havocesp/PathExt>
 - Created: 2023-07-28
"""
from setuptools import find_packages, setup

setup(
    name='pathext',
    version='0.1.0',
    # packages=[''],
    package_dir={'': 'pathext'},
    packages=find_packages(exclude=['.idea*', 'build*', '*.vs', '*.vscode', '*.code', '*.atom', '*.mypy_cache', f'${__package__}.egg-info*', 'dist*', 'venv*', '*.__pycache__*', '*.tox*']),
    url='https://github.com/havocesp/pathext',
    license='UNLICENSE',
    keywords='',
    author='havocesp',
    author_email='10012416+havocesp@users.noreply.github.com',
    long_description='Built-in Path with super powers.',
    long_description_content_type='text',
    description='Built-in Path with super powers.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.14',
    ],
)
