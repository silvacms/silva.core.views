# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
from Products.Silva.tests import SilvaTestCase
from Testing.ZopeTestCase.zopedoctest.functional import http
from silva.core.interfaces.adapters import IViewerSecurity

import unittest
import base64

AUTH_TOKEN = '%s:%s' % ('manager', SilvaTestCase.user_password)
AUTH = {'Authorization': 'Basic %s' % base64.b64encode(AUTH_TOKEN)}

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


class HEADTestCase(SilvaTestCase.SilvaFunctionalTestCase):

    def check_headers(self, method, path, headers, expected_headers):
        request = '%s %s HTTP/1.1' % (method, path)
        for header in headers.items():
            request += '\r\n%s: %s' % header
        self.response = http(request)
        self.failUnless(self.response.header_output.status, 200)
        response_headers = self.response.header_output.headers
        for key, value in expected_headers.items():
            reply_value = response_headers.get(key, None)
            self.assertEquals(
                reply_value, value,
                'Invalid header for "%s", expected: "%s", was: "%s"' %
                    (key, value, reply_value))

    def test_silvaroot(self):
        self.check_headers('HEAD', '/root', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvaroot_auth(self):
        self.check_headers('HEAD', '/root', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvaroot_auth_private(self):
        self.__set_private(self.root)
        self.check_headers('HEAD', '/root', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvapublication(self):
        self.add_document(self.root, 'publication', 'Publication')
        self.check_headers('HEAD', '/root/publication', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvapublication_auth(self):
        self.add_document(self.root, 'publication', 'Publication')
        self.check_headers('HEAD', '/root/publication', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvapublication_auth_private(self):
        publication = self.add_document(self.root, 'publication', 'Publication')
        self.__set_private(publication)
        self.check_headers('HEAD', '/root/publication', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvadocument(self):
        self.add_document(self.root, 'document', 'Document')
        self.check_headers('HEAD', '/root/document', {}, PUBLIC_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def test_silvadocument_auth(self):
        self.add_document(self.root, 'document', 'Document')
        self.check_headers('HEAD', '/root/document', AUTH, PUBLIC_HEADERS_EXPECTED)
        self.assertEquals("", self.response.getBody(), "response should be empty")
        self.assertEmptyResponse()

    def test_silvadocument_auth_private(self):
        document = self.add_document(self.root, 'document', 'Document')
        self.__set_private(document)
        self.check_headers('HEAD', '/root/document', AUTH, PRIVATE_HEADERS_EXPECTED)
        self.assertEmptyResponse()

    def __set_private(self, context):
        vs = IViewerSecurity(context)
        vs.setMinimumRole('Authenticated')
    
    def assertEmptyResponse(self):
        self.assertEquals("", self.response.getBody(), "response should be empty")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HEADTestCase))
    return suite
