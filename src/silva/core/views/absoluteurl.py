# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.component import queryMultiAdapter
from zope.interface import implements

# Zope 2
from Products.Five import BrowserView
from Acquisition import aq_parent

from silva.core.interfaces import IRoot, IContent, IVersionedContent
from silva.core.views.interfaces import IPreviewLayer, IContentURL
from silva.core.views.interfaces import IDisableBreadcrumbTag


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
    implements(IContentURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_virtual_root(self, path):
        virtual_path = self.request.physicalPathToVirtualPath(path)
        return not virtual_path

    def title(self, preview=False):
        if preview:
            return self.context.get_previewable().get_short_title()
        return self.context.get_short_title()

    def ancestors(self, preview=False, skip=None):
        name = minimize(self.title(preview=preview))
        container = aq_parent(self.context)
        if skip is not None:
            while skip.providedBy(container):
                container = aq_parent(container)

        if (container is None or
            IRoot.providedBy(self.context) or
            self.is_virtual_root(self.context.getPhysicalPath())):
            return ({'name': name, 'url': self.__str__()},)

        base = tuple()
        parent = queryMultiAdapter((container, self.request), IContentURL)
        if parent is not None:
            base = tuple(parent.ancestors(preview, skip))

        if (not IDisableBreadcrumbTag.providedBy(self.context) and
            (not IContent.providedBy(self.context) or
             not self.context.is_default())):
            base += ({'name': name, 'url': self.__str__()},)

        return base

    def url(self, preview=False, relative=False):
        # Insert back the preview namespace. Maybe there is a better
        # way to do it, but have to do it by hand here since
        # ZPublisher.Request doesn't implements its interfaces
        # properly.
        path = self.context.getPhysicalPath()
        request = self.request

        if preview is True:
            # Handle preview.
            root = self.context.get_root()
            root_path = root.getPhysicalPath()
            virtual_path = request.other.get('VirtualRootPhysicalPath', ('',))
            preview_pos = max(len(root_path), len(virtual_path))
            path = list(path)
            path.insert(preview_pos, "++preview++")
        return request.physicalPathToURL(path, relative=relative)

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url(preview=IPreviewLayer.providedBy(self.request))

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        return self.ancestors(
            skip=None,
            preview=IPreviewLayer.providedBy(self.request))


class VersionAbsoluteURL(AbsoluteURL):
    """AbsoluteURL for a version
    """

    def title(self, preview=False):
        return self.context.get_short_title()

    def breadcrumbs(self):
        return self.ancestors(
            skip=IVersionedContent,
            preview=IPreviewLayer.providedBy(self.request))


class ErrorAbsoluteURL(AbsoluteURL):
    """AbsoluteURL for a version
    """

    def __init__(self, context, request):
        # Set first Silva object as context
        self.context = context.get_silva_object()
        self.request = request


class TestAbsoluteURL(BrowserView):
    """An absolute URL provider for TestRequest. This is mainly to get
    test working.
    """
    implements(IContentURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False, relative=False):
        is_root = True
        if self.context is not None:
            path = list(self.context.getPhysicalPath())
            is_root = len(path) < (preview is True and 4 or 3)
            if preview is True:
                path.insert(2, '++preview++')
        if is_root:
            url = u'/root'
        else:
            url = u'/'.join(path)
        if relative:
            return url
        return u'http://localhost' + url

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url()

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        return tuple()
