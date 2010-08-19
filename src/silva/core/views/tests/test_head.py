# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import FunctionalLayer, http
from silva.core.interfaces.adapters import IAccessSecurity

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

    def check_headers(self, method, path, headers, expected_headers):
        request = '%s %s HTTP/1.1' % (method, path)
        for header in headers.items():
            request += '\r\n%s: %s' % header
        self.response = http(request, parsed=True)
        self.failUnless(self.response.getStatus(), 200)
        response_headers = self.response.getHeaders()
        for key, value in expected_headers.items():
            reply_value = response_headers.get(key, None)
            self.assertEquals(
                reply_value, value,
                'Invalid header for "%s", expected: "%s", was: "%s"' %
                    (key, value, reply_value))

    def set_private(self, context):
        IAccessSecurity(context).minimum_role = 'Authenticated'

    def assertEmptyResponse(self):
        self.assertEquals(
            "", self.response.getBody(), "response should be empty")

    def test_root(self):
        self.check_headers('HEAD', '/root', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_root_auth(self):
        self.check_headers('HEAD', '/root', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_root_auth_private(self):
        self.set_private(self.root)
        self.check_headers('HEAD', '/root', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_publication(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.check_headers(
            'HEAD', '/root/publication', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_publication_auth(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.check_headers(
            'HEAD', '/root/publication', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_publication_auth_private(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.set_private(self.root.publication)
        self.check_headers(
            'HEAD', '/root/publication', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_document(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        self.check_headers(
            'HEAD', '/root/document', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_document_auth(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        self.check_headers(
            'HEAD', '/root/document', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEquals(
            "", self.response.getBody(), "response should be empty")
        self.assertEmptyResponse()

    def test_document_auth_private(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        self.set_private(self.root.document)
        self.check_headers(
            'HEAD', '/root/document', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HEADTestCase))
    return suite
