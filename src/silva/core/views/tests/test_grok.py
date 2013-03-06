# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import doctest

from Products.Silva.testing import FunctionalLayer, suite_from_package

globs = {'grok': FunctionalLayer.grok,
         'getBrowser': FunctionalLayer.get_browser,
         'getRootFolder': FunctionalLayer.get_application}


def create_test(build_test_suite, name):
    test =  build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = FunctionalLayer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suite_from_package(
            'silva.core.views.tests.grok', create_test))
    return suite
