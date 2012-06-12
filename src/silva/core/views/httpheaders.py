# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae.wsgi.interfaces import IPublicationAfterRender
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.auth import IAccessSecurity

from .interfaces import IHTTPResponseHeaders, IHTTPHeaderView, INonCachedLayer


@grok.subscribe(IPublicationAfterRender)
def set_headers(event):
    #print event.content
    headers = queryMultiAdapter(
        (event.request, event.content),
        IHTTPResponseHeaders)
    if headers is not None:
        headers()


@grok.adapter(IBrowserRequest, IHTTPHeaderView)
@grok.implementer(IHTTPResponseHeaders)
def view_headers(request, view):
    return getMultiAdapter((request, view.context), IHTTPResponseHeaders)


class ResponseHeaders(grok.MultiAdapter):
    """Default class to implement HTTP header settings.
    """
    grok.baseclass()

    max_age = 86400

    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.response = request.response

    def cachable(self):
        return True

    def cache_headers(self):
        if self.cachable():
            self.response.setHeader(
                'Cache-Control',
                'max-age=%d, must-revalidate' % self.max_age)
        else:
            self.response.setHeader(
                'Cache-Control',
                'no-cache, must-revalidate, post-check=0, pre-check=0')
            self.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
            self.response.setHeader('Pragma', 'no-cache')

    def other_headers(self, headers):
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'text/html;charset=utf-8'
        for key, value in headers.items():
            self.response.setHeader(key, value)

    def set_headers(self, **headers):
        """Set the headers on the response.
        """
        self.cache_headers()
        self.other_headers(headers)

    def __call__(self, **headers):
        self.set_headers(**headers)


class ErrorHeaders(ResponseHeaders):
    """Errors are not cached.
    """
    grok.adapts(IBrowserRequest, Exception)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    def cachable(self):
        return False


class HTTPResponseHeaders(ResponseHeaders):
    """Regular Silva content headers.
    """
    grok.adapts(IBrowserRequest, ISilvaObject)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    def cachable(self):
        cachable = not (self._is_preview() or self._is_private())
        #print 'Set cachable', self.context, cachable
        return cachable

    def _is_preview(self):
        return INonCachedLayer.providedBy(self.request)

    def _is_private(self):
        return IAccessSecurity(self.context).minimum_role is not None
