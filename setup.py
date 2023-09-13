# See LICENSE.txt for license details.
# Copyright (c) 2011-2014 Simplistix Ltd, 2016 onwards Chris Withers
from setuptools import setup, find_packages

setup(
    name='configurator',
    version='3.2.0',
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
        toml=['tomli; python_version < "3.11"'],
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
        build=['sphinx', 'furo', 'setuptools-git', 'twine', 'wheel']
    ),
)
