# See license.txt for license details.
# Copyright (c) 2011-2014 Simplistix Ltd, 2016 Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='archivist',
    version='0.0.dev0',
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="Tools for YAML-based configuration files.",
    long_description=open('docs/description.rst').read(),
    url='https://github.com/Simplistix/configurator',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'voluptuous',
    ],
    extras_require=dict(
        test=[
            'testfixtures',
            'nose',
            'nose-cov',
            'mock',
            'coveralls',
            'mailinglogger',
            ],
        build=['sphinx', 'pkginfo', 'setuptools-git', 'twine', 'wheel']
    ),
)
