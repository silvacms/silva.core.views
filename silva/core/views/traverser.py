# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.SilvaLayout.adapters.traverser import SkinSetterMixin

from zope import component
from silva.core.views.interfaces import IHTTPResponseHeaders


class SilvaPublishTraverse(DefaultPublishTraverse):

    def browserDefault(self, request):
        # We don't want to lookup five views if we have other than a
        # GET or POST request.
        if request.method in ('GET', 'POST',):
            return super(SilvaPublishTraverse, self).browserDefault(request)
        if request.method in ('HEAD',):
            info = component.getMultiAdapter(
                (self.context, self.request), IHTTPResponseHeaders)
            return  info, ('set_headers',)
        return self.context, ()


class SilvaPubPublishTraverse(SilvaPublishTraverse, SkinSetterMixin):

    def publishTraverse(self, request, name):
        self._setSkin(request)
        return super(SilvaPubPublishTraverse, self).publishTraverse(
            request, name)

    def browserDefault(self, request):
        self._setSkin(request)
        return super(SilvaPubPublishTraverse, self).browserDefault(request)

