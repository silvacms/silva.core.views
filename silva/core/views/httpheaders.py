from five import grok
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.datetime import rfc1123_date
from AccessControl import getSecurityManager
from Products.Silva.interfaces import ISilvaObject
from Products.Silva.adapters.interfaces import IViewerSecurity
from silva.core.views.interfaces import IHTTPResponseHeaders


class HTTPResponseHeaders(grok.MultiAdapter):
    grok.adapts(ISilvaObject, IBrowserRequest)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    max_age = 86400

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = request.response

    def cache_headers(self):
        vs = IViewerSecurity(self.context)
        is_private = vs.getMinimumRole() != 'Anonymous'
        if is_private:
            # No cache when private
            self.response.setHeader(
                'Cache-Control',
                'no-cache, must-revalidate, post-check=0, pre-check=0')
            self.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
            self.response.setHeader('Pragma', 'no-cache')
        else:
            self.response.setHeader(
                'Cache-Control',
                'max-age=%d, must-revalidate' % self.max_age)

    def other_headers(self, headers):
        default = {'Content-Type': 'text/html;charset=utf-8'}
        headers.update(default)
        for key, value in headers.items():
            self.response.setHeader(key, value)

    def set_headers(self, **headers):
        """Set the headers on the response. Called directly to
        implement HEAD requests as well.
        """
        self.cache_headers()
        self.other_headers(headers)
        return ''
        
    def __is_preview(self):
        self.request

    def __call__(self, **headers):
        self.set_headers(**headers)
