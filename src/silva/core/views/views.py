# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl.security import checkPermission
from AccessControl import Unauthorized

from five import grok
from grokcore.layout import Layout as BaseLayout
from grokcore.layout import Page as BasePage
from grokcore.layout.interfaces import IPage
from zope import component
from zope.cachedescriptors.property import CachedProperty
from zope.viewlet.interfaces import IViewletManager

from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import IZMIView
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IView, IHTTPResponseHeaders


# Simple views


class HTTPHeaderView(object):
    """Support to set HTTP headers and support HEAD requests on views
    objects.

    This is not aimed to be use directly.
    """

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + (self.__name__,)

    def publishTraverse(self, request, name):
        if request.method == name and hasattr(self, name):
            return getattr(self, name)
        return super(HTTPHeaderView, self).publishTraverse(request, name)

    def browserDefault(self, request):
        if request.method in ('HEAD',):
            if hasattr(self, request.method):
                return self, (request.method,)
        return super(HTTPHeaderView, self).browserDefault(request)

    def setHTTPHeaders(self):
        headers = component.queryMultiAdapter(
            (self.request, self.context), IHTTPResponseHeaders)
        if headers is not None:
            headers.set_headers()

    def HEAD(self):
        """Reply to HEAD requests.
        """
        self.setHTTPHeaders()
        return ''

    def __call__(self):
        """Render the view.
        """
        self.setHTTPHeaders()
        return super(HTTPHeaderView, self).__call__()


class ZMIView(HTTPHeaderView, grok.View):
    """View in ZMI.
    """
    grok.baseclass()
    grok.require('zope2.ViewManagementScreens')
    grok.implements(IZMIView)


class Layout(BaseLayout):
    """A layout object.
    """
    grok.baseclass()
    grok.context(ISilvaObject)


class Page(HTTPHeaderView, BasePage):
    """A page class using a layout to render itself.
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.require('zope2.View')


_marker = object()

class View(HTTPHeaderView, grok.View):
    """View on Silva object, support view and preview
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IView)
    grok.name(u'content.html')
    grok.require('zope2.View')

    __content = _marker

    @CachedProperty
    def is_preview(self):
        return IPreviewLayer.providedBy(self.request)

    @apply
    def content():

        def getter(self):
            if self.__content is not _marker:
                return self.__content
            content = None
            if self.is_preview:
                content = self.context.get_previewable()
                if not checkPermission('silva.ReadSilvaContent', self.context):
                    raise Unauthorized(
                        "You need to be authenticated to access this version")
            if content is None:
                content = self.context.get_viewable()
            self.__content = content
            return content

        def setter(self, content):
            self.__content = content

        return property(getter, setter)

    def namespace(self):
        return {'content': self.content}


class ViewletLayoutSupport(object):
    """This add layout on the object and namespace if the view is an
    page.
    """

    def __init__(self, *args):
        super(ViewletLayoutSupport, self).__init__(*args)
        self.layout = None
        if IPage.providedBy(self.view):
            self.layout = self.view.layout

    def default_namespace(self):
        namespace = super(ViewletLayoutSupport, self).default_namespace()
        if self.layout:
            namespace['layout'] = self.layout
        return namespace


class ViewletManager(ViewletLayoutSupport, grok.ViewletManager):
    """A viewlet manager in Silva.
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IViewletManager)


class ContentProvider(ViewletManager):
    """A content provider in Silva. In fact it's just a viewlet
    manager...
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IContentProvider)

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace


class Viewlet(ViewletLayoutSupport, grok.Viewlet):
    """A viewlet in Silva
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IViewlet)
    grok.require('zope2.View')


__all__ = [
    'View', 'ZMIView', 'Layout', 'Page',
    'ContentProvider', 'ViewletManager', 'Viewlet']
