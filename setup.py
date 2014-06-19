# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Database",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
]

install_requires = [
    'redis',
]
if sys.version_info < (2, 7):
    install_requires.append('unittest2')


setup(
    name='testing.redis',
    version='1.0.2',
    description='automatically setups a redis instance in a temporary directory, and destroys it after testing',
    long_description=open('README.rst').read(),
    classifiers=classifiers,
    keywords=[],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='http://bitbucket.org/tk0miya/testing.redis',
    license='Apache License 2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=install_requires,
    extras_require=dict(
        testing=[
            'mock',
            'nose',
        ],
    ),
    test_suite='nose.collector',
    tests_require=[
        'mock',
        'nose',
    ],
)
