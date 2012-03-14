# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.component import getMultiAdapter
from zope.interface import implements

# Zope 2
from Products.Five import BrowserView
from Acquisition import aq_parent

from silva.core.interfaces import IRoot, IContent
from silva.core.views.interfaces import IPreviewLayer, ISilvaURL


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

    def title(self, preview=False):
        if preview:
            return self.context.get_previewable().get_short_title()
        return self.context.get_short_title()

    def path2url(self, path, preview=False):
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
            path = list(path)
            path.insert(preview_pos, self._preview_ns)
        return self.request.physicalPathToURL(path)

    def url(self, preview=False):
        return self.path2url(
            self.context.getPhysicalPath(),
            preview=preview)

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url(preview=IPreviewLayer.providedBy(self.request))

    __call__ = __repr__ = __unicode__ = __str__

    def is_virtual_root(self, content):
        path = content.getPhysicalPath()
        virtual_path = self.request.physicalPathToVirtualPath(path)
        return not virtual_path

    def breadcrumbs(self):
        container = aq_parent(self.context)
        preview = IPreviewLayer.providedBy(self.request)
        name = minimize(self.title(preview=preview))

        if (container is None or
            IRoot.providedBy(self.context) or
            self.is_virtual_root(self.context)):
            return ({'name': name, 'url': self.__str__()},)

        base = tuple(getMultiAdapter(
            (container, self.request), name='absolute_url').breadcrumbs())

        if IContent.providedBy(self.context) and not self.context.is_default():
            base += ({'name': name, 'url': self.__str__()},)

        return base


class VersionAbsoluteURL(AbsoluteURL):
    """AbsoluteURL for a version
    """

    def title(self, preview=False):
        return self.context.get_short_title()


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
