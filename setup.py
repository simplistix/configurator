# See license.txt for license details.
# Copyright (c) 2011-2014 Simplistix Ltd, 2016-2022 Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='configurator',
    version='3.0.0',
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
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
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
)
