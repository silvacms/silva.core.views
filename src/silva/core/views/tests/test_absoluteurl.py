# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.interface import alsoProvides
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope import component

from Products.Silva.testing import FunctionalLayer

from silva.core.views.interfaces import ISilvaURL
from silva.core.views.interfaces import IPreviewLayer


def enable_preview(content):
    """Enable preview mode.
    """
    if not IPreviewLayer.providedBy(content.REQUEST):
        alsoProvides(content.REQUEST, IPreviewLayer)


class PublicationAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', u'Test Publication')

    def test_url(self):
        url = component.getMultiAdapter((self.root.publication, self.root.REQUEST), ISilvaURL)
        self.assertTrue(verifyObject(ISilvaURL, url))
        self.assertTrue(ISilvaURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/publication')
        self.assertEqual(
            url(),
            'http://localhost/root/publication')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++/publication')

        enable_preview(self.root)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++/publication')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++/publication')

    def test_breadcrumbs(self):
        url = component.getMultiAdapter((self.root.publication, self.root.REQUEST), ISilvaURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root', 'name': 'root'},
             {'url': 'http://localhost/root/publication', 'name': u'Test Publication'}))

        enable_preview(self.root)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++', 'name': 'root'},
             {'url': 'http://localhost/root/++preview++/publication', 'name': u'Test Publication'}))

    def test_traverse(self):
        url = self.root.publication.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(ISilvaURL, url))


class RootAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_url(self):
        url = component.getMultiAdapter((self.root, self.root.REQUEST), ISilvaURL)
        self.assertTrue(verifyObject(ISilvaURL, url))
        self.assertTrue(ISilvaURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root')
        self.assertEqual(
            url(),
            'http://localhost/root')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++')

        enable_preview(self.root)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++')

    def test_breadcrumbs(self):
        url = component.getMultiAdapter((self.root, self.root.REQUEST), ISilvaURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root', 'name': 'root'},))

        enable_preview(self.root)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++', 'name': 'root'},))

    def test_traverse(self):
        url = self.root.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(ISilvaURL, url))


class VersionedContentAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', u'Test Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Folder')
        factory = self.root.publication.folder.manage_addProduct['Silva']
        factory.manage_addLink('link', u'Link')

    def test_url(self):
        content = self.root.publication.folder.link
        url = component.getMultiAdapter((content, self.root.REQUEST), ISilvaURL)
        self.assertTrue(verifyObject(ISilvaURL, url))
        self.assertTrue(ISilvaURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/publication/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/publication/folder/link')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++/publication/folder/link')

        enable_preview(self.root)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++/publication/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++/publication/folder/link')

    def test_breadcrumbs(self):
        content = self.root.publication.folder.link
        url = component.getMultiAdapter((content, self.root.REQUEST), ISilvaURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root', 'name': u'root'},
             {'url': 'http://localhost/root/publication', 'name': u'Test Publication'},
             {'url': 'http://localhost/root/publication/folder', 'name': u'Folder'},
             {'url': 'http://localhost/root/publication/folder/link', 'name': u'link'}))

        enable_preview(self.root)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++', 'name': u'root'},
             {'url': 'http://localhost/root/++preview++/publication', 'name': u'Test Publication'},
             {'url': 'http://localhost/root/++preview++/publication/folder', 'name': u'Folder'},
             {'url': 'http://localhost/root/++preview++/publication/folder/link', 'name': u'Link'}))

    def test_traverse(self):
        content = self.root.publication.folder.link
        url = content.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(ISilvaURL, url))


class VersionContentAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', u'Test Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Folder')
        factory = self.root.publication.folder.manage_addProduct['Silva']
        factory.manage_addLink('link', u'Link with like a completely super long title to test them')

    def test_url(self):
        content = self.root.publication.folder.link.get_editable()
        url = component.getMultiAdapter((content, self.root.REQUEST), ISilvaURL)
        self.assertTrue(verifyObject(ISilvaURL, url))
        self.assertTrue(ISilvaURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/publication/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/publication/folder/link')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++0/publication/folder/link')

        enable_preview(self.root)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++0/publication/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++0/publication/folder/link')

    def test_breadcrumbs(self):
        content = self.root.publication.folder.link.get_editable()
        url = component.getMultiAdapter((content, self.root.REQUEST), ISilvaURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root', 'name': u'root'},
             {'url': 'http://localhost/root/publication', 'name': u'Test Publication'},
             {'url': 'http://localhost/root/publication/folder', 'name': u'Folder'},
             {'url': 'http://localhost/root/publication/folder/link',
              'name': u'Link with like a completely super long title to...'}))

        enable_preview(self.root)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++', 'name': 'root'},
             {'url': 'http://localhost/root/++preview++/publication', 'name': u'Test Publication'},
             {'url': 'http://localhost/root/++preview++/publication/folder', 'name': u'Folder'},
             {'url': 'http://localhost/root/++preview++0/publication/folder/link',
              'name': u'Link with like a completely super long title to...'}))

    def test_traverse(self):
        content = self.root.publication.folder.link.get_editable()
        url = content.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(ISilvaURL, url))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(RootAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionedContentAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionContentAbsoluteURLTestCase))
    return suite


