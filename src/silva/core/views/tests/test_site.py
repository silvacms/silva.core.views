# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt


import unittest

from silva.core.views.interfaces import IVirtualSite
from zope.interface.verify import verifyObject
from zope.component import getAdapter

from Products.Silva.testing import FunctionalLayer, TestRequest


class VirtualSiteTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_virtualsite_root(self):
        request = TestRequest(application=self.root)
        site = getAdapter(request, IVirtualSite)
        self.assertTrue(verifyObject(IVirtualSite, site))
        self.assertEqual(site.get_root(), self.root)
        self.assertEqual(site.get_root_url(), 'http://localhost/root')
        self.assertEqual(site.get_root_path(), '/root')

        # We have a direct root
        self.assertEqual(site.get_silva_root(), self.root)
        self.assertEqual(site.get_virtual_root(), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VirtualSiteTestCase))
    return suite
