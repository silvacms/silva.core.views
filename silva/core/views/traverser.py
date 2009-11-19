# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable
from silva.core.views.interfaces import IHTTPResponseHeaders

from five import grok

from ZPublisher.BaseRequest import DefaultPublishTraverse
from silva.core.interfaces import IPublication

from silva.core.views.interfaces import IPreviewLayer

class PreviewTraversable(grok.MultiAdapter):
    """Traverser to display versioned contents in SMI preview.
    
    Add the preview layer on the request if needed.
    """
    grok.adapts(IPublication, IBrowserRequest)
    grok.implements(ITraversable)
    grok.name('preview')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, remaining):
        if not IPreviewLayer.providedBy(self.request):
            alsoProvides(self.request, IPreviewLayer)
        return self.context


class SilvaPublishTraverse(DefaultPublishTraverse):

    def browserDefault(self, request):
        response_headers = \
            getMultiAdapter((self.context, self.request),
                            IHTTPResponseHeaders)
        response_headers()
        if request.method == 'HEAD':
            return SilvaHead(self.context, request)
        # We don't want to lookup five views if we have other than a
        # GET or POST request.
        if request.method in ('GET', 'POST',):
            return super(SilvaPublishTraverse, self).browserDefault(request)
        return self.context, ()


class SilvaHead(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return ""


