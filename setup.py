# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='redsolutioncms.django-generic-ratings',
    version=__import__('ratings').__version__,
    description=read('DESCRIPTION'),
    author='Francesco Banconi',
    author_email='francesco.banconi@gmail.com',
    url='https://bitbucket.org/frankban/django-generic-ratings/downloads',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    entry_points={
        'redsolutioncms': ['ratings = ratings.redsolution_setup', ],
    }
)
