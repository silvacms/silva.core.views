# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.interface import alsoProvides
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope import component

from Products.Silva.testing import FunctionalLayer, TestRequest

from silva.core.views.interfaces import IContentURL
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IDisableBreadcrumbTag


class PublicationAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('section', u'Test Publication')

    def test_url(self):
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (self.root.section, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/section')
        self.assertEqual(
            url(),
            'http://localhost/root/section')
        self.assertEqual(
            url.url(relative=True),
            '/root/section')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/root/++preview++/section')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++/section')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++/section')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++/section')

    def test_breadcrumbs(self):
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (self.root.section, request), IContentURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root',
              'name': u'root'},
             {'url': 'http://localhost/root/section',
              'name': u'Test Publication'}))

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++',
              'name': u'root'},
             {'url': 'http://localhost/root/++preview++/section',
              'name': u'Test Publication'}))

    def test_traverse(self):
        url = self.root.section.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


class RootAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_url(self):
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter((self.root, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root')
        self.assertEqual(
            url(),
            'http://localhost/root')
        self.assertEqual(
            url.url(relative=True),
            '/root')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/root/++preview++')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++')

    def test_breadcrumbs(self):
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (self.root, request), IContentURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root',
              'name': u'root'},))

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++',
              'name': u'root'},))

    def test_traverse(self):
        url = self.root.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


class VersionedContentAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('section', u'Test Publication')
        factory = self.root.section.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Folder')
        factory = self.root.section.folder.manage_addProduct['Silva']
        factory.manage_addLink('link', u'Link')

    def test_url(self):
        content = self.root.section.folder.link
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (content, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/section/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/section/folder/link')
        self.assertEqual(
            url.url(relative=True),
            '/root/section/folder/link')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/root/++preview++/section/folder/link')
        self.assertEqual(
            url.url(preview=True),
            'http://localhost/root/++preview++/section/folder/link')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++/section/folder/link')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++/section/folder/link')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++/section/folder/link')

    def test_breadcrumbs(self):
        """Test the breacrumb computation for a regular versioned content.
        """
        content = self.root.section.folder.link
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (content, request),
            IContentURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root',
              'name': u'root'},
             {'url': 'http://localhost/root/section',
              'name': u'Test Publication'},
             {'url': 'http://localhost/root/section/folder',
              'name': u'Folder'},
             {'url': 'http://localhost/root/section/folder/link',
              'name': u'link'}))

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++',
              'name': u'root'},
             {'url': 'http://localhost/root/++preview++/section',
              'name': u'Test Publication'},
             {'url': 'http://localhost/root/++preview++/section/folder',
              'name': u'Folder'},
             {'url': 'http://localhost/root/++preview++/section/folder/link',
              'name': u'Link'}))

    def test_disable_breacrumbs(self):
        """Test that you can hide a content from the breadcrumbs using
        a marker interface.
        """
        alsoProvides(self.root.section, IDisableBreadcrumbTag)
        alsoProvides(self.root.section.folder, IDisableBreadcrumbTag)
        content = self.root.section.folder.link
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter((content, request), IContentURL)

        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root',
              'name': u'root'},
             {'url': 'http://localhost/root/section/folder/link',
              'name': u'link'}))

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++',
              'name': u'root'},
             {'url': 'http://localhost/root/++preview++/section/folder/link',
              'name': u'Link'}))

    def test_traverse(self):
        content = self.root.section.folder.link
        url = content.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


class VersionAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('section', u'Test Publication')
        factory = self.root.section.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Folder')
        factory = self.root.section.folder.manage_addProduct['Silva']
        factory.manage_addLink(
            'link',
            u'Link with like a completely super long title to test them')

    def test_url(self):
        content = self.root.section.folder.link.get_editable()
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (content, request),
            IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/section/folder/link/0')
        self.assertEqual(
            url(),
            'http://localhost/root/section/folder/link/0')
        self.assertEqual(
            url.url(relative=True),
            '/root/section/folder/link/0')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/root/++preview++/section/folder/link/0')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/++preview++/section/folder/link/0')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/++preview++/section/folder/link/0')
        self.assertEqual(
            url(),
            'http://localhost/root/++preview++/section/folder/link/0')

    def test_breadcrumbs(self):
        """Test breadcrumb computation when it is directly called on a
        given vesion.
        """
        content = self.root.section.folder.link.get_editable()
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (content, request),
            IContentURL)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root',
              'name': u'root'},
             {'url': 'http://localhost/root/section',
              'name': u'Test Publication'},
             {'url': 'http://localhost/root/section/folder',
              'name': u'Folder'},
             {'url': 'http://localhost/root/section/folder/link/0',
              'name': u'Link with like a completely super long title to...'}))

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            url.breadcrumbs(),
            ({'url': 'http://localhost/root/++preview++',
              'name': u'root'},
             {'url': 'http://localhost/root/++preview++/section',
              'name': u'Test Publication'},
             {'url': 'http://localhost/root/++preview++/section/folder',
              'name': u'Folder'},
             {'url': 'http://localhost/root/++preview++/section/folder/link/0',
              'name': u'Link with like a completely super long title to...'}))

    def test_traverse(self):
        content = self.root.section.folder.link.get_editable()
        url = content.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(RootAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionedContentAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionAbsoluteURLTestCase))
    return suite


