# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

import os
from ConfigParser import RawConfigParser
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

# read test requirements from tox.ini
config = RawConfigParser()
config.read(os.path.join(base_dir, 'tox.ini'))
test_requires = []
for item in config.get('testenv', 'deps').split():
    test_requires.append(item)
# Tox doesn't need itself, but we need it for testing.
test_requires.append('tox')

setup(
    name='configurator',
    author='Chris Withers',
    version='1.0dev',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="A general purpose library for handling configuration stores.",
    long_description=open(os.path.join(base_dir,'docs','description.txt')).read(),
    url='http://www.simplistix.co.uk/software/python/configurator',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        ],    
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        test=test_requires,
        )
    )
