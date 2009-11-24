from five import grok
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Silva.interfaces import ISilvaObject
from Products.Silva.adapters.interfaces import IViewerSecurity
from silva.core.views.interfaces import IHTTPResponseHeaders


class ResponseHeaderHandler(grok.MultiAdapter):

    grok.baseclass()

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = request.response
        self.response.setHeader('Content-Type', 'text/html;charset=utf-8')

    def cache_headers(self):
        pass

    def other_headers(self, headers):
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
    grok.adapts(Exception, IBrowserRequest)
    grok.implements(IHTTPResponseHeaders)
    grok.provides(IHTTPResponseHeaders)

    def cache_headers(self):
        self.disable_cache()


class HTTPResponseHeaders(ResponseHeaderHandler):
    grok.adapts(ISilvaObject, IBrowserRequest)
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
        return self.request.URL.endswith('preview_html')

    def __is_private(self):
        vs = IViewerSecurity(self.context)
        return vs.getMinimumRole() != 'Anonymous'


