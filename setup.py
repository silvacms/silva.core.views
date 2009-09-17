# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.2b1'

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
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
              'setuptools',
              'zope.interface',
              'zope.schema',
              'five.grok',
              'five.megrok.z3cform',
              'five.megrok.layout',
              'plone.z3cform > 0.5.2',
              'silva.core.conf',
              ],
      )
