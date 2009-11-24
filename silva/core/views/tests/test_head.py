from Products.Silva.tests import SilvaTestCase
from Testing.ZopeTestCase.zopedoctest.functional import http
from Products.Silva.adapters.interfaces import IViewerSecurity

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

    def check_headers(self, path, headers, expected_headers):
        request = 'HEAD %s HTTP/1.1' % path
        for header in headers.items():
            request += '\r\n%s: %s' % header
        reply = http(request)
        self.failUnless(reply.header_output.status, 200)
        reply_headers = reply.header_output.headers
        for key, value in expected_headers.items():
            reply_value = reply_headers.get(key, None)
            self.assertEquals(
                reply_value, value,
                'Invalid header for "%s", expected: "%s", was: "%s"' %
                    (key, value, reply_value))

    def test_silvaroot(self):
        self.check_headers('/root', {}, PUBLIC_HEADERS_EXPECTED)

    def test_silvaroot_auth(self):
        self.check_headers('/root', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_silvaroot_auth_private(self):
        self.__set_private(self.root)
        self.check_headers('/root', AUTH, PRIVATE_HEADERS_EXPECTED)

    def test_silvapublication(self):
        self.add_document(self.root, 'publication', 'Publication')
        self.check_headers('/root/publication', {}, PUBLIC_HEADERS_EXPECTED)

    def test_silvapublication_auth(self):
        self.add_document(self.root, 'publication', 'Publication')
        self.check_headers('/root/publication', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_silvapublication_auth_private(self):
        publication = self.add_document(self.root, 'publication', 'Publication')
        self.__set_private(publication)
        self.check_headers('/root/publication', AUTH, PRIVATE_HEADERS_EXPECTED)

    def test_silvadocument(self):
        self.add_document(self.root, 'document', 'Document')
        self.check_headers('/root/document', {}, PUBLIC_HEADERS_EXPECTED)

    def test_silvadocument_auth(self):
        self.add_document(self.root, 'document', 'Document')
        self.check_headers('/root/document', AUTH, PUBLIC_HEADERS_EXPECTED)

    def test_silvadocument_auth_private(self):
        document = self.add_document(self.root, 'document', 'Document')
        self.__set_private(document)
        self.check_headers('/root/document', AUTH, PRIVATE_HEADERS_EXPECTED)

    def __set_private(self, context):
        vs = IViewerSecurity(context)
        vs.setMinimumRole('Authenticated')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HEADTestCase))
    return suite
