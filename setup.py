#! /usr/bin/env python
from setuptools import setup

import woodstock
setup(
    name='woodstock',
    version = woodstock.__version__,
    description = 'django based event toolkit',
    author = 'Marc Egli',
    author_email = 'egli@allink.ch',
    url = 'http://github.com/allink/woodstock/',
    packages=[
        'woodstock',
    ],
    package_data={'woodstock':'templates/*.html'},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    requires=[
        'Django(>=1.2.1)',
    ],
    
)