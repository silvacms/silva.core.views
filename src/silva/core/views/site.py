# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from infrae.wsgi.interfaces import IRequest, IVirtualHosting
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.http import IHTTPRequest
from zope.site.hooks import getSite

from silva.core.views.interfaces import IVirtualSite, IContentURL


class VirtualSite(grok.Adapter):
    grok.implements(IVirtualSite)
    grok.provides(IVirtualSite)
    grok.context(IHTTPRequest)

    def __init__(self, request):
        self.request = request
        self._url = None

    def _get_url(self):
        if self._url is None:
            root = self.get_root()
            if root is not None:
                self._url = queryMultiAdapter((root, self.request), IContentURL)
        return self._url

    def get_root(self):
        root = self.get_virtual_root()
        if root is None:
            return self.get_silva_root()
        return root

    def get_root_path(self):
        url = self._get_url()
        if url is not None:
            return url.url(relative=True)
        return u''

    get_top_level_path = get_root_path

    def get_root_url(self):
        url = self._get_url()
        if url is not None:
            return url.url()
        return u''

    get_top_level_url = get_root_url

    def get_silva_root(self):
        # We call get_root to by pass any local site
        site = getSite()
        if site is not None:
            return site.get_root()
        return None

    def get_virtual_root(self):
        return None


class WSGIVirtualSite(VirtualSite):
    grok.context(IRequest)

    def get_virtual_root(self):
        plugin = self.request.get_plugin(IVirtualHosting)
        if plugin is not None:
            return plugin.root
        return None
