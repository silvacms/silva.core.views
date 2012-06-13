# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable

from Acquisition.interfaces import IAcquirer
from ZPublisher.BaseRequest import DefaultPublishTraverse

from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.views import HEADView


class UseParentByAcquisition(object):
    """Request traverseName which query the ITraversable adapter always
    do a __of__ of the result of the queried adapter to get the new
    context object to use afterward. It is annoying if you don't want
    to change of context object, as if you return the same object you
    got in input it will have __of__ of himself.

    Returning an instance of this object will prevent that behavior
    and permit you to stay on the same context object.
    """
    grok.implements(IAcquirer)

    def __of__(self, obj):
        return obj


class PreviewTraversable(grok.MultiAdapter):
    """Traverser to display versioned contents in SMI preview.

    Add the preview layer on the request if needed.
    """
    grok.adapts(ISilvaObject, IBrowserRequest)
    grok.implements(ITraversable)
    grok.name('preview')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, remaining):
        if not IPreviewLayer.providedBy(self.request):
            alsoProvides(self.request, IPreviewLayer)
        return UseParentByAcquisition()


class SilvaPublishTraverse(DefaultPublishTraverse):

    def browserDefault(self, request):
        # We don't want to lookup five views if we have other than a
        # GET or POST request.
        if request.method in ('GET', 'POST',):
            return super(SilvaPublishTraverse, self).browserDefault(request)
        if request.method == 'HEAD':
            return HEADView(self.context, request, self.context), tuple()
        return self.context, tuple()

