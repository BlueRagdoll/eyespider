#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='eyespider',
    version='1.0.0',
    author='Chuck Huang',
    description="A simple,qiuck scraping micro-framework",
    author_email='chuckhunagcm@gmail.com',
    install_requires=['lxml', 'requests', 'cchardet', 'cssselect'],
    url="https://github.com/howie6879/eyespider/README.md",
    packages=find_packages(),
    package_data={'eyespider': ['utils/*.txt']})
