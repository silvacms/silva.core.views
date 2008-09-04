# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3

import zope.component
from zope.interface import implements

# Zope 2
from OFS.interfaces import ITraversable
from Products.Five import BrowserView

from Products.Silva.interfaces import IPublication, IRoot

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
        # Insert back the preview namespace. Maybe there is a better way to do it.
        if preview:
            root = self.context.get_root()
            root_path = root.getPhysicalPath()
            path.insert(len(root_path), '++preview++')
        return self.request.physicalPathToURL(path)

    def preview(self):
        return self.url(preview=True)

    def __str__(self):
        return self.url(preview=IPreviewLayer.providedBy(self.request))

    __call__ = __repr__ = __str__

    def breadcrumbs(self):
        context = self.context.aq_inner
        container = context.aq_parent
        request = self.request

        name = context.get_short_title()
        
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

        base += ({'name': name, 'url': self.__str__()},)

        return base

