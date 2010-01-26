# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate
from zope.publisher.publish import mapply
from zope.viewlet.interfaces import IViewletManager

from grokcore.view.meta.views import default_view_name
import urllib

from Products.Silva.interfaces import ISilvaObject

from silva.core.conf.utils import getSilvaViewFor
from silva.core.layout.interfaces import ISMILayer
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import IFeedback, IZMIView, ISMIView, ISMITab
from silva.core.views.interfaces import IView, IHTTPResponseHeaders

from five import grok
from five.megrok.layout import Layout as BaseLayout
from five.megrok.layout import Page as BasePage
from megrok.layout.interfaces import IPage

from AccessControl import getSecurityManager
from zExceptions import Unauthorized
import Acquisition

# Simple views

class SilvaErrorSupplement(object):
    """Add more information about an error on a view in a traceback.
    """

    def __init__(self, klass, full_information=False):
        self.context = klass.context
        self.request = klass.request
        self.klass = klass
        self.full_information = full_information

    def getInfo(self, as_html=0):
        object_path = '/'.join(self.context.getPhysicalPath())
        info = list()
        info.append((u'Class', '%s.%s' % (
                    self.klass.__module__, self.klass.__class__.__name__)))
        info.append((u'Object path', object_path,))
        info.append((u'Object type', getattr(self.context, 'meta_type', None,)))
        if self.full_information:
            request_value = lambda x: self.request.get(x, 'n/a')
            info.append((u'Request URL',
                         request_value('URL'),))
            info.append((u'Request method',
                         request_value('method'),))
            info.append((u'Authenticated user',
                         request_value('AUTHENTICATED_USER'),))
            info.append((u'User-agent',
                         request_value('HTTP_USER_AGENT'),))
            info.append((u'Referer',
                         request_value('HTTP_REFERER'),))

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
        if request.method == name and hasattr(self.aq_base, name):
            return getattr(self.aq_base, name)
        return super(SilvaGrokView, self).publishTraverse(request, name)

    def browserDefault(self, request):
        if request.method in ('HEAD',):
            if hasattr(self.aq_base, request.method):
                return self, (request.method,)
        return super(SilvaGrokView, self).browserDefault(request)

    def setHTTPHeaders(self):
        headers = component.queryMultiAdapter(
            (self.context, self.request), IHTTPResponseHeaders)
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
        __traceback_supplement__ = (SilvaErrorSupplement, self, False)
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


class ZMIForm(grok.Form, ZMIView):
    """A simple form in ZMI.
    """

    grok.baseclass()

    # ZMI Templates requires Zope2 engine.
    template = grok.PageTemplate(filename='templates/zmi_form.pt')


class ZMIEditForm(grok.EditForm, ZMIView):
    """An edit form in ZMI.
    """

    grok.baseclass()

    # ZMI Templates requires Zope2 engine.
    template = grok.PageTemplate(filename='templates/zmi_form.pt')


class SMIView(SilvaGrokView):
    """A view in SMI.
    """

    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(ISMIView)

    vein = 'contents'

    def __init__(self, context, request):
        super(SMIView, self).__init__(context, request)

        # Set model on request like silvaviews
        self.request['model'] = self._silvaContext
        if hasattr(self, 'template') and self.template is not None:
            # Set id on template some macros uses template/id
            self.template._template.id = self.__view_name__

    @CachedProperty
    def _silvaContext(self):
        context = self.context
        while not ISilvaObject.providedBy(context) and \
                hasattr(context, 'context'):
            context = context.context
        return context.aq_inner

    def _silvaView(self):
        # Lookup the correct Silva edit view so forms are able to use
        # silva macros.
        context = self._silvaContext
        return getSilvaViewFor(self.context, 'edit', context)

    @CachedProperty
    def silvaviews(self):
        # XXX should be removed when silva stop to do stupid things
        # with view in templates. This give access to the silvaviews
        # directory from the view itself.
        return self._silvaView()

    @property
    def tab_name(self):
        return grok.name.bind().get(self, default=default_view_name)

    @property
    def active_tab(self):
        tab_class = None
        for base in self.__class__.__bases__:
            if ISMITab.implementedBy(base):
                tab_class = base
        if tab_class:
            name = grok.name.bind()
            return name.get(tab_class, default=default_view_name)
        return 'tab_edit'

    def namespace(self):
        # This add to the template namespace global variable used in
        # Zope 2 and Silva templates.  Here should be bind at the
        # correct place in the Silva view registry so you should be
        # able to use silva macro in your templates.
        return {'here': self.silvaviews,
                'user': getSecurityManager().getUser(),
                'realview': self, # XXX should be removed when silva
                                  # stop to do stupid things with view
                                  # in templates.
                'container': self._silvaContext.aq_inner,}

    def provider(self, name):
        # XXX should be removed when Silva stop to do stupid with view
        # in templates
        context = self._silvaContext
        provider =  component.getMultiAdapter(
            (context, self.request, self), name=name)
        provider = provider.__of__(context)
        provider.update()
        return provider.render()


class Layout(BaseLayout):
    """A layout object.
    """

    grok.baseclass()
    grok.context(ISilvaObject)

    def __call__(self, view):
        """Render the layout.
        """
        __traceback_supplement__ = (SilvaErrorSupplement, self, False)
        return super(Layout, self).__call__(view)


class Page(BasePage):
    """A page class using a layout to render itself.
    """

    grok.baseclass()
    grok.context(ISilvaObject)
    grok.require('zope2.View')

    def __call__(self):
        """Render the page.
        """
        __traceback_supplement__ = (SilvaErrorSupplement, self, True)
        return super(Page, self).__call__()


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
        # Preview in 2.1 is different.
        url = self.request.URL
        return 'preview_html' in url

    @CachedProperty
    def content(self):
        if self.is_preview:
            return self.context.get_previewable()
        return self.context.get_viewable()

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

    grok.view(SMIView)

    template = grok.PageTemplate(filename='templates/smiportletmanager.pt')

    def enabled(self):
        return len(self.viewlets) != 0
