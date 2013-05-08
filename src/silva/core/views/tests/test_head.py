# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IAccessSecurity, IHTTPHeadersSettings
from zope.interface.verify import verifyObject

import unittest

AUTH = {
    'Authorization': 'Basic manager:manager'}

PUBLIC_HEADERS_EXPECTED = {
    'Last-Modified': None,
    'X-Powered-By': 'SilvaCMS',
    'Content-Length': '0',
    'Content-Type': 'text/html;charset=utf-8',
    'Cache-Control': 'max-age=86400, must-revalidate'}
PRIVATE_HEADERS_EXPECTED = {
    'Last-Modified': None,
    'X-Powered-By': 'SilvaCMS',
    'Content-Length': '0',
    'Expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
    'Content-Type': 'text/html;charset=utf-8',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache, must-revalidate, post-check=0, pre-check=0'}


class HEADTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def assertHeadersEqual(self, path, headers, expected_headers):
        with self.layer.get_browser() as browser:
            # Set request header
            for name, value in headers.items():
                browser.set_request_header(name, value)

            self.assertEqual(browser.open(path, method='HEAD'), 200)
            self.assertEqual(browser.contents, '')

            # Check result headers
            for name, value in expected_headers.items():
                self.assertIn(name, browser.headers,
                              'Missing header for "%s"' % name)
                if value is not None:
                    reply_value = browser.headers.get(name)
                    self.assertEquals(
                        reply_value, value,
                        'Invalid header for "%s", expected: "%s", was: "%s"' %
                        (name, value, reply_value))

    check_headers = assertHeadersEqual

    def set_private(self, context):
        IAccessSecurity(context).minimum_role = 'Authenticated'


class SilvaHEADTestCase(HEADTestCase):
    """Test HEAD request on default Silva content.
    """

    def test_root(self):
        self.assertHeadersEqual(
            '/root', {}, PUBLIC_HEADERS_EXPECTED)

    def test_root_authorized(self):
        self.assertHeadersEqual(
            '/root', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_root_authorized_and_restriscted(self):
        self.set_private(self.root)
        self.assertHeadersEqual(
            '/root', AUTH, PRIVATE_HEADERS_EXPECTED)

    def test_publication(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.assertHeadersEqual(
            '/root/publication', {}, PUBLIC_HEADERS_EXPECTED)

    def test_publication_settings(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        settings = IHTTPHeadersSettings(self.root.publication)
        settings.http_disable_cache = True
        self.assertTrue(verifyObject(IHTTPHeadersSettings, settings))
        self.assertHeadersEqual(
            '/root/publication', {}, PRIVATE_HEADERS_EXPECTED)

    def test_publication_authorized(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.assertHeadersEqual(
            '/root/publication', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_publication_authorized_and_restricted(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.set_private(self.root.publication)
        self.assertHeadersEqual(
            '/root/publication', AUTH, PRIVATE_HEADERS_EXPECTED)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaHEADTestCase))
    return suite
