# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

#python
import re

# Zope 3
from zope.component import getMultiAdapter
from zope.interface import implements

# Zope 2
from OFS.interfaces import ITraversable
from Products.Five import BrowserView
from Acquisition import aq_parent

from silva.core.interfaces import IRoot, IContent, IContainer
from silva.core.views.interfaces import IPreviewLayer, ISilvaURL, IVirtualSite


def minimize(string):
    """Minize a string to 50 characters.
    """
    string = string.strip()
    if len(string) > 50:
        return string[:47].strip() + '...'
    return string


class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.traversing.browser.absoluteurl)
    """
    implements(ISilvaURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._preview_ns = '++preview++'

        def title():
            if IPreviewLayer.providedBy(self.request):
                return context.get_previewable().get_short_title()
            return context.get_short_title()

        self.title = title

    def url(self, preview=False):
        path = list(self.context.getPhysicalPath())
        # Insert back the preview namespace. Maybe there is a better
        # way to do it, but have to do it by hand here since
        # ZPublisher.Request doesn't implements its interfaces
        # properly.
        if preview is True:
            root = self.context.get_root()
            root_path = root.getPhysicalPath()
            virtual_path = self.request.other.get(
                'VirtualRootPhysicalPath', ('',))
            preview_pos = max(len(root_path), len(virtual_path))
            path.insert(preview_pos, self._preview_ns)
        url = self.request.physicalPathToURL(path)
        return url

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url(preview=IPreviewLayer.providedBy(self.request))

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        container = aq_parent(self.context)
        name = minimize(self.title())
        virtual_root = IVirtualSite(self.request).get_root()

        def isVirtualHostRoot():
            return self.context == virtual_root

        if (container is None or
            IRoot.providedBy(self.context) or
            isVirtualHostRoot() or
            not ITraversable.providedBy(container)):
            return ({'name': name, 'url': self.__str__(), 'id':self.context.id, 'obj': self.context},)

        base = tuple(getMultiAdapter(
                (container, self.request), name='absolute_url').breadcrumbs())

        if not (IContent.providedBy(self.context) and self.context.is_default()):
            base += ({'name': name, 'url': self.__str__(), 'id':self.context.id, 'obj': self.context},)

        return base


class VersionAbsoluteURL(AbsoluteURL):
    """AbsoluteURL for a version
    """

    def __init__(self, context, request):
        # Set versioned content as context
        self.context = context.get_content()
        self.request = request
        self._preview_ns = '++preview++' + context.getId()
        self.title = lambda: context.get_short_title()


class ErrorAbsoluteURL(AbsoluteURL):
    """AbsoluteURL for a version
    """

    def __init__(self, context, request):
        # Set first Silva object as context
        self.context = context.get_silva_object()
        self.request = request
        self._preview_ns = '++preview++'


class TestAbsoluteURL(BrowserView):
    """An absolute URL provider for TestRequest. This is mainly to get
    test working.
    """

    implements(ISilvaURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False):
        is_root = True
        if self.context is not None:
            path = list(self.context.getPhysicalPath())
            is_root = len(path) < (preview is True and 4 or 3)
            if preview is True:
                path.insert(2, '++preview++')
        if is_root:
            return u'http://localhost/root'
        return u'http://localhost' + '/'.join(path)

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url()

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        return tuple()
