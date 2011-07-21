#! /usr/bin/env python
import os
from setuptools import setup

import woodstock
setup(
    name='woodstock',
    version = woodstock.__version__,
    description = 'django based event toolkit',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author = 'Marc Egli',
    author_email = 'egli@allink.ch',
    url = 'http://github.com/allink/woodstock/',
    license='BSD License',
    platforms=['OS Independent'],
    packages=[
        'woodstock',
        'woodstock.content',
        'woodstock.content.event',
        'woodstock.feincms_extensions',
        'woodstock.models',
        'woodstock.templatetags',
        'woodstock.urls',
        'woodstock.views',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    requires=[
        'FeinCMS(>=1.3.0)',
        'Django(>=1.3)',
        'pennyblack(>=0.2.1)',
        'icalendar(>=2.1)',
    ],
    include_package_data=True,    
    
)