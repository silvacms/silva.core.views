# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from infrae.wsgi.interfaces import IPublicationAfterRender
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from webdav.common import rfc1123_date
from silva.core.interfaces import IHTTPHeadersSettings
from silva.core.interfaces import ISilvaObject, IVersion
from silva.core.interfaces.auth import IAccessSecurity

from .interfaces import IHTTPResponseHeaders, IHTTPHeaderView
from .interfaces import INonCachedLayer


@grok.subscribe(IPublicationAfterRender)
def set_headers(event):
    headers = queryMultiAdapter(
        (event.request, event.content),
        IHTTPResponseHeaders)
    if headers is not None:
        headers()


@grok.adapter(IBrowserRequest, IHTTPHeaderView)
@grok.implementer(IHTTPResponseHeaders)
def view_headers(request, view):
    return queryMultiAdapter((request, view.context), IHTTPResponseHeaders)


class ResponseHeaders(grok.MultiAdapter):
    """Default class to implement HTTP header settings.
    """
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)
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
            current = self.response.headers.get('Content-Type')
            if not current or current == 'text/html':
                # Don't override existing content types, except for
                # html that doesn't specify a charset (code source
                # breakage).
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

    def cachable(self):
        return False


class HTTPResponseHeaders(ResponseHeaders):
    """Regular Silva content headers.
    """
    grok.adapts(IBrowserRequest, ISilvaObject)

    def __init__(self, request, context):
        settings = IHTTPHeadersSettings(context, None)
        self._force_disable_cachable = False
        self._include_last_modified = True
        if settings is not None:
            self.max_age = settings.http_max_age
            self._force_disable_cachable = settings.http_disable_cache
            self._include_last_modified = settings.http_last_modified
        super(HTTPResponseHeaders, self).__init__(request, context)

    def cachable(self):
        if self._force_disable_cachable:
            return False
        return not (self._is_preview() or self._is_private())

    def _is_preview(self):
        return INonCachedLayer.providedBy(self.request)

    def _is_private(self):
        return IAccessSecurity(self.context).minimum_role is not None

    def other_headers(self, headers):
        if self._include_last_modified and 'Last-Modified' not in headers:
            # If missing, add a last-modified header with the modification time.
            modification = self.context.get_modification_datetime()
            if modification is not None:
                self.response.setHeader(
                    'Last-Modified',
                    rfc1123_date(modification))
        super(HTTPResponseHeaders, self).other_headers(headers)


class HTTPResponseVersionHeaders(ResponseHeaders):
    """Regular Silva version headers.
    """
    grok.adapts(IBrowserRequest, IVersion)

    def cachable(self):
        # Views on version are not cachable by default.
        return False
