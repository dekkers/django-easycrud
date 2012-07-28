#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'django-easycrud',
    version = '0.1',
    description = "Easy creation of django CRUD apps",
     author = 'Jeroen Dekkers',
    author_email = 'jeroen@dekkers.ch',
    url='https://github.com/dekkers/django-easycrud/',
    packages = find_packages(),
    include_package_data = True,
)
