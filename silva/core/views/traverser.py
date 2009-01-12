# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable

from five import grok

from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.Silva.interfaces import IPublication

from silva.core.views.interfaces import IPreviewLayer

class PreviewTraversable(grok.MultiAdapter):

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
        # We don't want to lookup five views if we have other than a
        # GET or POST request.
        if request.method in ['GET', 'POST',]:
            return super(SilvaPublishTraverse, self).browserDefault(request)
        return self.context, ()
