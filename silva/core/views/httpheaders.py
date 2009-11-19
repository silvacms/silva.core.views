from five import grok
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.datetime import rfc1123_date
from AccessControl import getSecurityManager

from Products.Silva.interfaces import ISilvaObject
from silva.core.views.interfaces import IHTTPResponseHeaders


class HTTPResponseHeaders(grok.MultiAdapter):

    grok.adapts(ISilvaObject, IBrowserRequest)
    grok.implements(IHTTPResponseHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = request.response

    def cache_headers(self):
        authenticated = getSecurityManager().getUser().has_role('Authenticated')
        is_preview = 'preview_html' in self.request['URL']
        if is_preview:
            content = self.context.get_previewable()
        else:
            content = self.context.get_viewable()
        if content is not None:
            mod_date = content.get_modification_datetime()
            self.response.setHeader('Last-Modified', rfc1123_date(mod_date))
        if is_preview or authenticated:
            # No cache when in preview mode
            self.response.setHeader(
                'Cache-Control',
                'no-cache, must-revalidate, post-check=0, pre-check=0')
            self.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
            self.response.setHeader('Pragma', 'no-cache')
        else:
            self.response.setHeader(
                'Cache-Control','max-age=7200, must-revalidate')

    def content_type_headers(self):
        self.response.setHeader('Content-Type', 'text/html;charset=utf-8')

    def __call__(self):
        self.cache_headers()
        self.content_type_headers()
