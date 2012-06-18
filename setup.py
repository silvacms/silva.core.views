# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '3.0dev'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.core.views',
      version=version,
      description="Views and forms support for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva core views',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Zope2',
        'five.grok [layout]',
        'grokcore.layout',
        'grokcore.view',
        'grokcore.viewlet',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'zope.cachedescriptors',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.deferredimport',
        'zope.interface',
        'zope.publisher',
        'zope.site',
        'zope.traversing',
        'zope.viewlet',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
