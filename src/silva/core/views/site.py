# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.site.hooks import getSite
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
        root = self.get_root()
        if root is not None:
            return absoluteURL(root, self.request)
        return u''

    def get_silva_root(self):
        # Return Silva root, using getSite and acquisition
        site = getSite()
        if site:
            return site.get_root()
        return None

    def get_virtual_root(self):
        root_path = self.get_virtual_path()
        if root_path is None:
            return None

        return getSite().restrictedTraverse(root_path, None)

    def get_virtual_path(self):
        try:
            root_path = self.request['VirtualRootPhysicalPath']
        except (AttributeError, KeyError):
            root_path =  None

        return root_path

