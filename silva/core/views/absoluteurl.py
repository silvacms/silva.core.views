# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3

import zope.component
from zope.interface import implements

# Zope 2
from OFS.interfaces import ITraversable
from Products.Five import BrowserView

from silva.core.interfaces import IRoot, IContent

from silva.core.views.interfaces import IPreviewLayer, ISilvaURL

class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.traversing.browser.absoluteurl)
    """

    implements(ISilvaURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False):
        path = list(self.context.getPhysicalPath())
        # Insert back the preview namespace. Maybe there is a better
        # way to do it.
        if preview:
            root = self.context.get_root()
            root_path = root.getPhysicalPath()
            virtual_path = self.request.other.get('VirtualRootPhysicalPath', ('',))
            preview_pos = max(len(root_path), len(virtual_path))
            path.insert(preview_pos, '++preview++')
        return self.request.physicalPathToURL(path)

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url(preview=IPreviewLayer.providedBy(self.request))

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        context = self.context.aq_inner
        container = context.aq_parent
        request = self.request

        name = context.get_short_title()
        if len(name) > 50:
            name = name[47:] + '...'

        def isVirtualHostRoot():
            path = self.context.getPhysicalPath()
            virtualPath = self.request.physicalPathToVirtualPath(path)
            return not virtualPath

        if (container is None or
            IRoot.providedBy(self.context) or
            isVirtualHostRoot() or
            not ITraversable.providedBy(container)):
            return ({'name': name, 'url': self.__str__()},)

        base = tuple(zope.component.getMultiAdapter(
                     (container, request), name='absolute_url').breadcrumbs())

        if not (IContent.providedBy(context) and context.is_default()):
            base += ({'name': name, 'url': self.__str__()},)

        return base


class TestAbsoluteURL(BrowserView):
    """An absolute URL provider for TestRequest. This is mainly to get
    test working.
    """

    implements(ISilvaURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False):
        return u'http://localhost/root'

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url()

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        return tuple()
