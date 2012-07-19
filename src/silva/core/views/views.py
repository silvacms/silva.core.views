# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl.security import checkPermission
from AccessControl import Unauthorized

from five import grok
from grokcore.layout.interfaces import IPage
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.cachedescriptors.property import CachedProperty
from zope.viewlet.interfaces import IViewletManager

from silva.core.interfaces import IViewableObject
from .interfaces import IContentProvider, IViewlet, IZMIView, IView
from .interfaces import IPreviewLayer, IRender
from .interfaces import IHTTPHeaderView

# Simple views

class HEADView(object):
    """View returned as the implementation of an HEAD request.
    """
    grok.implements(IHTTPHeaderView)

    def __init__(self, context, request, parent, name='HEAD'):
        self.context = context
        self.request = request
        self.__parent__ = parent
        self.__name__ = name

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + (self.__name__,)

    def __call__(self, *args, **kwargs):
        return u''


class HTTPHeaderView(object):
    """Support to set HTTP headers and support HEAD requests on views
    objects.

    This is not aimed to be use directly.
    """
    grok.implements(IHTTPHeaderView)

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + (self.__name__,)

    def publishTraverse(self, request, name):
        if request.method == name and name in ['HEAD',]:
            return HEADView(self.context, request, self)
        return super(HTTPHeaderView, self).publishTraverse(request, name)

    def browserDefault(self, request):
        if request.method in ('HEAD',):
            return HEADView(self.context, request, self), tuple()
        return super(HTTPHeaderView, self).browserDefault(request)


class ZMIView(HTTPHeaderView, grok.View):
    """View in ZMI.
    """
    grok.baseclass()
    grok.require('zope2.ViewManagementScreens')
    grok.implements(IZMIView)


class Render(object):
    grok.baseclass()
    grok.context(Interface)
    grok.provides(IRender)
    grok.implements(IRender)
    grok.name('view')

    def __init__(self, context, request):
        self.context = context
        self.request = request


    def default_namespace(self):
        return {}

    def namespace(self):
        return {'view': self,
                'context': self.context,
                'request': self.request}

    def update(self, *args, **kwargs):
        pass

    def render(self, *args, **kwargs):
        return self.template.render(self)

    render.base_method = True

    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self.render(*args, **kwargs)

_marker = object()


def render(context, request, name="view"):
    view =  getMultiAdapter((context, request), IRender, name)
    return view()


class View(HTTPHeaderView, grok.View):
    """View on Silva object, support view and preview
    """
    grok.baseclass()
    grok.context(IViewableObject)
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


class Page(HTTPHeaderView, grok.Page):
    """A page class using a layout to render itself.
    """
    grok.baseclass()
    grok.context(IViewableObject)
    grok.require('zope2.View')


class Layout(grok.Layout):
    """A layout object.
    """
    grok.baseclass()
    grok.context(IViewableObject)


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
    grok.context(IViewableObject)
    grok.implements(IViewletManager)


class ContentProvider(ViewletManager):
    """A content provider in Silva. In fact it's just a viewlet
    manager...
    """
    grok.baseclass()
    grok.context(IViewableObject)
    grok.implements(IContentProvider)

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace


class Viewlet(ViewletLayoutSupport, grok.Viewlet):
    """A viewlet in Silva
    """
    grok.baseclass()
    grok.context(IViewableObject)
    grok.implements(IViewlet)
    grok.require('zope2.View')


__all__ = [
    'View', 'ZMIView', 'Layout', 'Page',
    'ContentProvider', 'ViewletManager', 'Viewlet']
