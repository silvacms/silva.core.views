# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_base

from five import grok
from infrae.layout import Layout as BaseLayout
from infrae.layout import Page as BasePage
from infrae.layout.interfaces import IPage
from zope import component
from zope.component.interfaces import ComponentLookupError
from zope.cachedescriptors.property import CachedProperty
from zope.viewlet.interfaces import IViewletManager
import zope.deferredimport
from zope.publisher.publish import mapply

from silva.core.interfaces import (ISilvaObject, IContainer, IContentLayout,
                                   IVersionedContentLayout, 
                                   IDefaultContentTemplate)
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import IZMIView
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IView, IHTTPResponseHeaders
from silva.core.smi.interfaces import ISMILayer

zope.deferredimport.deprecated(
    'SMIView moved to silva.core.smi. '
    'Consider using a SMIPage instead. It will be removed in Silva 2.4',
    SMIView='silva.core.smi.smi:SMIView')
zope.deferredimport.deprecated(
    'SMIPortletManager moved to silva.core.smi.smi. '
    'Please update your import. This one will be removed in Silva 2.4',
    SMIPortletManager='silva.core.smi.smi:SMIPortletManager')


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
            #use __call__ instead of setupHeaders directly. to enable
            # adapters in lower skins/layers to override in the __call__ method
            headers.__call__()

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

class ContentTemplateMixin(object):
    """Mixin class to assist pages and views in wrapping the rendered
       content around a content layout template if necessary"""
    
    def wrap_if_necessary(self, rendered_content):
        """Wrap the rendered content around a default content template if
           necessary"""
        obj = self.context
        #do not wrap rendered content if in edit mode (i.e. ISMILayer)
        # this can happen when the content/screen is a zeam SMIForm
        if ISMILayer.providedBy(self.request):
            return rendered_content
        #if this is the default view (i.e. index.html) of a container,
        # get the default document.  Default views will likely NOT be
        # overridden (why not just use a silvaviews.View then?) but there
        # are grok Views registered on interfaces attached to containers
        # which DO change the default template.
        # there SHOULD NOT be extra views registered on ContentLayout objects.
        if self.__name__ == 'index.html' and IContainer.providedBy(obj):
            #if a container, need to get the default document, since containers
            # don't implement contentlayout
            if obj.get_default():
                obj = obj.get_default()
        if not (IContentLayout.providedBy(obj) or \
                IVersionedContentLayout.providedBy(obj)):
            #does not provide content layout (but may still need to 
            # be rendered within a content layout)
            # render the content, inject into default content renderer view
            try:
                dcl = component.getMultiAdapter((obj,
                                                 self.request),
                                                interface=IDefaultContentTemplate)
            except ComponentLookupError:
                return rendered_content
            dcl.rendered_content = rendered_content
            return dcl()
        return rendered_content
        
    
class Page(HTTPHeaderView, BasePage, ContentTemplateMixin):
    """A page class using a layout to render itself.
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.require('zope2.View')
    
    def content(self):
        """override BasePage's method to provide content layout support"""
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        
        content = mapply(self.render, (), self.request)
        return self.wrap_if_necessary(content)
    
class View(HTTPHeaderView, grok.View):
    """View on Silva object, support view and preview
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IView)
    grok.name(u'content.html')
    grok.require('zope2.View')

    @CachedProperty
    def is_preview(self):
        return IPreviewLayer.providedBy(self.request)

    @CachedProperty
    def content(self):
        preview_name = self.request.other.get('SILVA_PREVIEW_NAME', None)
        if (preview_name is not None and
            hasattr(aq_base(self.context), preview_name)):
            return getattr(self.context, preview_name)
        version = None
        if self.is_preview:
            version = self.context.get_previewable()
        if version is None:
            version = self.context.get_viewable()
        return version

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
