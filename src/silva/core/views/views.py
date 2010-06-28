# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from five.megrok.layout import Layout as BaseLayout
from five.megrok.layout import Page as BasePage
from megrok.layout.interfaces import IPage, ILayout
from zope import component, interface
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate
from zope.viewlet.interfaces import IViewletManager
import zope.deferredimport

from AccessControl import getSecurityManager
from Acquisition import aq_base
from ZPublisher.mapply import mapply

import urllib

from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import ILayoutFactory
from silva.core.views.interfaces import IFeedback, IZMIView
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IView, IHTTPResponseHeaders

zope.deferredimport.deprecated(
    'Please import from silva.core.smi.smi instead,'
    'this import will be removed in Silva 2.4',
    SMIView='silva.core.smi.smi:SMIView')


# Simple views

class SilvaErrorSupplement(object):
    """Add more information about an error on a view in a traceback.
    """

    def __init__(self, klass, full_information=False):
        self.context = klass.context
        self.request = klass.request
        self.klass = klass

    def getInfo(self, as_html=0):
        object_path = u'n/a'
        if hasattr(aq_base(self.context), 'getPhysicalPath'):
            object_path = '/'.join(self.context.getPhysicalPath())
        info = list()
        info.append(
            (u'Class', '%s.%s' % (
                    self.klass.__module__, self.klass.__class__.__name__)))
        info.append(
            (u'Object path', object_path,))
        info.append(
            (u'Object type', getattr(self.context, 'meta_type', u'n/a',)))
        if not as_html:
            return '   - ' + '\n   - '.join(map(lambda x: '%s: %s' % x, info))

        from cgi import escape
        return u'<p>Extra information:<br /><li>%s</li></p>' % ''.join(map(
            lambda x: u'<li><b>%s</b>: %s</li>' % (
                escape(str(x[0])), escape(str(x[1]))),
            info))


class SilvaGrokView(grok.View):
    """Grok View on Silva objects.
    """
    grok.baseclass()

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + ('/@@' + self.__name__,)

    def publishTraverse(self, request, name):
        if request.method == name and hasattr(self, name):
            return getattr(self, name)
        return super(SilvaGrokView, self).publishTraverse(request, name)

    def browserDefault(self, request):
        if request.method in ('HEAD',):
            if hasattr(self, request.method):
                return self, (request.method,)
        return super(SilvaGrokView, self).browserDefault(request)

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
        __traceback_supplement__ = (SilvaErrorSupplement, self)
        self.setHTTPHeaders()
        return super(SilvaGrokView, self).__call__()

    def redirect(self, url):
        # Override redirect to send status information if there is.
        if IFeedback.providedBy(self):
            message = self.status
            if message:
                message = translate(message)
                if isinstance(message, unicode):
                    # XXX This won't be decoded correctly at the other end.
                    message = message.encode('utf8')
                to_append = urllib.urlencode(
                    {'message': message, 'message_type': self.status_type,})
                join_char = '?' in url and '&' or '?'
                super(SilvaGrokView, self).redirect(url + join_char + to_append)
                return
        super(SilvaGrokView, self).redirect(url)


class ZMIView(SilvaGrokView):
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

    def __call__(self, view):
        """Render the layout.
        """
        __traceback_supplement__ = (SilvaErrorSupplement, self)
        return super(Layout, self).__call__(view)


class LayoutFactory(grok.MultiAdapter):
    grok.adapts(interface.Interface, interface.Interface)
    grok.implements(ILayoutFactory)
    grok.provides(ILayoutFactory)

    def __init__(self, request, context):
        self.request = request
        self.context = context

    def __call__(self, view):
        """ Default behavior of megrok.layout Page
        """
        return component.getMultiAdapter(
            (self.request, self.context), ILayout)


class Page(BasePage):
    """A page class using a layout to render itself.
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.require('zope2.View')

    def __call__(self):
        """Render the page.
        """
        __traceback_supplement__ = (SilvaErrorSupplement, self)

        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        layout_factory = component.getMultiAdapter(
            (self.request, self.context,), ILayoutFactory)
        self.layout = layout_factory(self)
        return self.layout(self)


class View(SilvaGrokView):
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
        if 'model' in self.request:
            return self.request['model']
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


class SMIPortletManager(ViewletManager):
    """Third SMI column manager.
    """
    grok.view(interface.Interface)

    def enabled(self):
        return len(self.viewlets) != 0
