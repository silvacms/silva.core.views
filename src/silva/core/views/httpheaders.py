# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.publisher.interfaces.browser import IBrowserRequest
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.adapters import IViewerSecurity
from silva.core.views.interfaces import IHTTPResponseHeaders, INonCachedLayer


class ResponseHeaderHandler(grok.MultiAdapter):
    """Default class to implement HTTP header settings.
    """
    grok.baseclass()

    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.response = request.response

    def cache_headers(self):
        pass

    def other_headers(self, headers):
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'text/html;charset=utf-8'
        for key, value in headers.items():
            self.response.setHeader(key, value)

    def set_headers(self, **headers):
        """Set the headers on the response. Called directly to
        implement HEAD requests as well.
        """
        self.cache_headers()
        self.other_headers(headers)
        return ''

    def __call__(self, **headers):
        return self.set_headers(**headers)

    def disable_cache(self):
        self.response.setHeader(
            'Cache-Control',
            'no-cache, must-revalidate, post-check=0, pre-check=0')
        self.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        self.response.setHeader('Pragma', 'no-cache')


class ErrorHeaders(ResponseHeaderHandler):
    """Errors are not cached.
    """
    grok.adapts(IBrowserRequest, Exception)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    def cache_headers(self):
        self.disable_cache()


class HTTPResponseHeaders(ResponseHeaderHandler):
    """Regular Silva content headers.
    """
    grok.adapts(IBrowserRequest, ISilvaObject)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    max_age = 86400

    def cache_headers(self):
        if self.__is_private() or self.__is_preview():
            # No cache when private
            self.disable_cache()
        else:
            self.response.setHeader(
                'Cache-Control',
                'max-age=%d, must-revalidate' % self.max_age)

    def __is_preview(self):
        return INonCachedLayer.providedBy(self.request)

    def __is_private(self):
        vs = IViewerSecurity(self.context)
        return vs.getMinimumRole() != 'Anonymous'


