# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces.auth import IAccessSecurity

import unittest

AUTH = {
    'Authorization': 'Basic manager:manager'}

PUBLIC_HEADERS_EXPECTED = {
    'Content-Length': '0',
    'Content-Type': 'text/html;charset=utf-8',
    'Cache-Control': 'max-age=86400, must-revalidate'}
PRIVATE_HEADERS_EXPECTED = {
    'Content-Length': '0',
    'Expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
    'Content-Type': 'text/html;charset=utf-8',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache, must-revalidate, post-check=0, pre-check=0'}


class HEADTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def check_headers(self, path, headers, expected_headers):
        with self.layer.get_browser() as browser:
            # Set request header
            for name, value in headers.items():
                browser.set_request_header(name, value)

            self.assertEqual(browser.open(path, method='HEAD'), 204)
            self.assertEqual(browser.contents, '')

            # Check result headers
            for name, value in expected_headers.items():
                reply_value = browser.headers.get(name)
                self.assertEquals(
                    reply_value, value,
                    'Invalid header for "%s", expected: "%s", was: "%s"' %
                        (name, value, reply_value))

    def set_private(self, context):
        IAccessSecurity(context).minimum_role = 'Authenticated'


class SilvaHEADTestCase(HEADTestCase):
    """Test HEAD request on default Silva content.
    """

    def test_root(self):
        self.check_headers('/root', {}, PUBLIC_HEADERS_EXPECTED)

    def test_root_auth(self):
        self.check_headers('/root', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_root_auth_private(self):
        self.set_private(self.root)
        self.check_headers('/root', AUTH, PRIVATE_HEADERS_EXPECTED)

    def test_publication(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.check_headers('/root/publication', {}, PUBLIC_HEADERS_EXPECTED)

    def test_publication_auth(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.check_headers('/root/publication', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_publication_auth_private(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.set_private(self.root.publication)
        self.check_headers('/root/publication', AUTH, PRIVATE_HEADERS_EXPECTED)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaHEADTestCase))
    return suite
