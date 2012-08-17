# -*- coding: utf-8 -*- 
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject
from zope.interface import alsoProvides
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope import component

from Products.Silva.testing import FunctionalLayer, TestRequest

from infrae.wsgi.interfaces import IVirtualHosting

from silva.core.views.interfaces import IContentURL
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IDisableBreadcrumbTag


class ServicesAbsoluteURLTestCase(unittest.TestCase):
    # This test the ContentURL adapter on Zope object.
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_url(self):
        """Test IContentURL url computation. Preview is not available
        on Zope object.
        """
        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (self.root.service_extensions, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://localhost/root/service_extensions')
        self.assertEqual(
            url(),
            'http://localhost/root/service_extensions')
        self.assertEqual(
            url.url(relative=True),
            '/root/service_extensions')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/root/service_extensions')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/service_extensions')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/service_extensions')
        self.assertEqual(
            url(),
            'http://localhost/root/service_extensions')

    def test_vhm(self):
        """Test IContentURL url computation while a VHM is used. Zope
        object doesn't support the preview mode.
        """
        request = TestRequest(
            application=self.root,
            url='http://localhost/service_extension',
            headers=[('X-VHM-Url', 'http://infrae.com'),
                     ('X-VHM-Path', '/root')])
        plugin = request.query_plugin(request.application, IVirtualHosting)
        root, method, path = plugin(request.method, request.path)
        self.assertEqual(root, self.root)
        self.assertEqual(method, 'index_html')
        self.assertEqual(path, ['service_extension'])

        url = component.getMultiAdapter(
            (self.root.service_extensions, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://infrae.com/service_extensions')
        self.assertEqual(
            url(),
            'http://infrae.com/service_extensions')
        self.assertEqual(
            url.url(relative=True),
            '/service_extensions')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/service_extensions')
        self.assertEqual(
            url.preview(),
            'http://infrae.com/service_extensions')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://infrae.com/service_extensions')
        self.assertEqual(
            url(),
            'http://infrae.com/service_extensions')

    def test_traverse(self):
        url = self.root.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


class BrainsAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('section', u'Test Publication')

    def test_url(self):
        """Test the IContentURL on Catalog brains object. Like for
        Zope object, they don't support the preview mode.
        """
        brains = self.root.service_catalog(
            meta_type="Silva Publication",
            path="/root/section")
        self.assertEqual(len(brains), 1)
        brain = brains[0]

        request = TestRequest(application=self.root)
        url = component.getMultiAdapter(
            (brain, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            brain.getURL(),
            'http://localhost/root/section')
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
            '/root/section')
        self.assertEqual(
            url.preview(),
            'http://localhost/root/section')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://localhost/root/section')
        self.assertEqual(
            url(),
            'http://localhost/root/section')

    def test_traverse(self):
        url = self.root.restrictedTraverse('@@absolute_url')
        self.assertTrue(verifyObject(IContentURL, url))


class PublicationAbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('section', u'Test Publication')

    def test_url(self):
        """Verify the IContentURL on a Silva Publication.
        """
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

    def test_vhm(self):
        """Test IContentURL url computation while a VHM is used.
        """
        request = TestRequest(
            application=self.root,
            url='http://localhost/section',
            headers=[('X-VHM-Url', 'http://infrae.com'),
                     ('X-VHM-Path', '/root')])
        plugin = request.query_plugin(request.application, IVirtualHosting)
        root, method, path = plugin(request.method, request.path)
        self.assertEqual(root, self.root)
        self.assertEqual(method, 'index_html')
        self.assertEqual(path, ['section'])

        url = component.getMultiAdapter(
            (self.root.section, request), IContentURL)
        self.assertTrue(verifyObject(IContentURL, url))
        self.assertTrue(IContentURL.extends(IAbsoluteURL))

        self.assertEqual(
            str(url),
            'http://infrae.com/section')
        self.assertEqual(
            url(),
            'http://infrae.com/section')
        self.assertEqual(
            url.url(relative=True),
            '/section')
        self.assertEqual(
            url.url(relative=True, preview=True),
            '/++preview++/section')
        self.assertEqual(
            url.preview(),
            'http://infrae.com/++preview++/section')

        alsoProvides(request, IPreviewLayer)
        self.assertEqual(
            str(url),
            'http://infrae.com/++preview++/section')
        self.assertEqual(
            url(),
            'http://infrae.com/++preview++/section')

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
    suite.addTest(unittest.makeSuite(ServicesAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(BrainsAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(PublicationAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(RootAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionedContentAbsoluteURLTestCase))
    suite.addTest(unittest.makeSuite(VersionAbsoluteURLTestCase))
    return suite


