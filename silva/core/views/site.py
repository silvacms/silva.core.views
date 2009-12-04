# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.app.component.hooks import getSite
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteURL

from silva.core.views.interfaces import IVirtualSite


class VirtualSite(grok.Adapter):
    grok.implements(IVirtualSite)
    grok.provides(IVirtualSite)
    grok.context(IHTTPRequest)

    def __init__(self, request):
        self.request = request

    def get_root(self):
        root = self.get_virtual_root()
        if root is None:
            return self.get_silva_root()
        return root

    def get_root_url(self):
        return absoluteURL(self.get_root(), self.request)

    def get_silva_root(self):
        # XXX Check for nested localsites in Silva
        return getSite()

    def get_virtual_root(self):
        root_path = self.get_virtual_path()
        if root_path is None:
            return None

        return getSite().restrictedTraverse(root_path, None)

    def get_virtual_path(self):
        try:
            root_path = self.request['VirtualRootPhysicalPath']
        except (AttributeError, KeyError), err:
            root_path =  None

        return root_path
