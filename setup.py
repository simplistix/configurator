# See license.txt for license details.
# Copyright (c) 2011-2014 Simplistix Ltd, 2016-2019 Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='configurator',
    version='1.0.0',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description=(
        "A library for building a configuration store "
        "from one or more layered configuration sources"
    ),
    long_description=open('README.rst').read(),
    url='https://github.com/Simplistix/configurator',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        yaml=['pyyaml'],
        toml=['toml'],
        test=[
            'jinja2',
            'mock',
            'pyfakefs',
            'pytest',
            'pytest-cov',
            'requests',
            'sybil',
            'testfixtures',
            'voluptuous',
        ],
        build=['sphinx', 'sphinx-rtd-theme', 'setuptools-git', 'twine', 'wheel']
    ),
    entry_points={
        'configurator.parser': [
            'json = json:load',
            'toml = toml:load',
            'yml = yaml:safe_load',
            'yaml = yaml:safe_load',
        ],
    }
)
