# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.i18n import translate
from zope.viewlet.interfaces import IViewletManager
from zope.cachedescriptors.property import CachedProperty
from zope.publisher.publish import mapply
import zope.component

from grokcore.view.meta.views import default_view_name
from five import grok
import urllib

from Products.Silva.interfaces import ISilvaObject

from silva.core.views.interfaces import IFeedback, IZMIView, ISMIView, ISMITab
from silva.core.views.interfaces import IView
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.layout.interfaces import ISMILayer
from silva.core.conf.utils import getSilvaViewFor

from five.megrok.layout import Page as BasePage
from five.megrok.layout import Layout as BaseLayout
from megrok.layout.interfaces import IPage

from AccessControl import getSecurityManager
import Acquisition

# Simple views

class SilvaGrokView(grok.View):
    """Grok View on Silva objects.
    """

    grok.baseclass()

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
        provider =  zope.component.getMultiAdapter(
            (context, self.request, self), name=name)
        provider = provider.__of__(context)
        provider.update()
        return provider.render()


class Layout(BaseLayout):
    """A layout object.
    """

    grok.baseclass()
    grok.context(ISilvaObject)


class Page(BasePage):
    """A page class using a layout to render itself.
    """

    grok.baseclass()
    grok.context(ISilvaObject)


class View(SilvaGrokView):
    """View on Silva object, support view and preview
    """

    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(IView)
    grok.name(u'content.html')

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



class SMIPortletManager(ViewletManager):
    """Third SMI column manager.
    """

    grok.view(SMIView)

    template = grok.PageTemplate(filename='templates/smiportletmanager.pt')

    def enabled(self):
        return len(self.viewlets) != 0
