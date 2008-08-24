# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
from zope.i18n import translate
from zope.contentprovider.interfaces import IContentProvider

from five import grok
import urllib

from Products.Silva.interfaces import ISilvaObject
from Products.SilvaLayout.interfaces import IPreviewLayer

from silva.core.views.interfaces import IFeedback, IZMIView, IView, ITemplate
from silva.core import conf as silvaconf

import Acquisition

# Simple views

class SilvaGrokView(grok.View):
    """Grok View on Silva objects.
    """

    silvaconf.baseclass()

    def publishTraverse(self, request, name):
        """In Zope2, if you give a name, index_html is appended to it.
        """
        if name == 'index_html':
            return self
        return super(View, self).publishTraverse(request, name)

    def redirect(self, url):
        # Override redirect to send status information if there is.
        if IFeedback.providedBy(self):
            message = self.status
            if message:
                message = translate(message)
                if isinstance(message, unicode):
                    # XXX This won't be decoded correctly at the other end.
                    message = message.encode('utf8')
                to_append = urllib.urlencode({'message': message,
                                              'message_type': self.status_type,})
                join_char = '?' in url and '&' or '?'
                super(SilvaGrokView, self).redirect(url + join_char + to_append)
                return
        super(SilvaGrokView, self).redirect(url)


class ZMIView(SilvaGrokView):
    """View in ZMI.
    """

    grok.implements(IZMIView)

    silvaconf.baseclass()

class Template(SilvaGrokView):
    """A view class not binded to a content.
    """

    grok.implements(ITemplate)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

class View(Template):
    """View on Silva object, support view and preview
    """

    grok.implements(IView)

    silvaconf.baseclass()
    silvaconf.name(u'content.html')

    @zope.cachedescriptors.property.CachedProperty
    def is_preview(self):
        return IPreviewLayer.providedBy(self.request)

    @zope.cachedescriptors.property.CachedProperty
    def content(self):
        if self.is_preview:
            return self.context.get_previewable()
        return self.context.get_viewable()

    def namespace(self):
        return {'content': self.content}


class ContentProvider(Acquisition.Implicit):

    grok.implements(IContentProvider)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.__name__ = self.__view_name__

    def default_namespace(self):
        namespace = {}
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    def render(self):
        return self.template.render(self)


from five.resourceinclude.provider import ResourceIncludeProvider

class ResourceContentProvider(ResourceIncludeProvider, ContentProvider):

    silvaconf.name('resources')
