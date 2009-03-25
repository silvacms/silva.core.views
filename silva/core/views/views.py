# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.i18n import translate
from zope.viewlet.interfaces import IViewletManager
from zope.cachedescriptors.property import CachedProperty

from grokcore.view.meta.views import default_view_name
from five import grok
import urllib

from Products.Silva.interfaces import ISilvaObject

from silva.core.views.interfaces import IFeedback, IZMIView, ISMIView, ISMITab
from silva.core.views.interfaces import ITemplate, IPreviewLayer, IView
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.layout.interfaces import ISMILayer
from silva.core.conf.utils import getSilvaViewFor
from silva.core import conf as silvaconf

from AccessControl import getSecurityManager

# Simple views

class SilvaGrokView(grok.View):
    """Grok View on Silva objects.
    """

    silvaconf.baseclass()

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
    silvaconf.require('zope2.ViewManagementScreens')


class ZMIForm(grok.Form, ZMIView):
    """A simple form in ZMI.
    """

    silvaconf.baseclass()

    # ZMI Templates requires Zope2 engine.
    template = grok.PageTemplate(filename='templates/zmi_form.pt')


class ZMIEditForm(grok.EditForm, ZMIView):
    """An edit form in ZMI.
    """

    silvaconf.baseclass()

    # ZMI Templates requires Zope2 engine.
    template = grok.PageTemplate(filename='templates/zmi_form.pt')


class SMIView(SilvaGrokView):
    """A view in SMI.
    """

    grok.implements(ISMIView)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)
    silvaconf.layer(ISMILayer)

    vein = 'contents'

    def __init__(self, context, request):
        super(SMIView, self).__init__(context, request)

        # Set model on request like SilvaViews
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

    @property
    def tab_name(self):
        return silvaconf.name.bind().get(self, default=default_view_name)

    @property
    def active_tab(self):
        tab_class = None
        for base in self.__class__.__bases__:
            if ISMITab.implementedBy(base):
                tab_class = base
        if tab_class:
            name = silvaconf.name.bind()
            return name.get(tab_class, default=default_view_name)
        return 'tab_edit'

    def namespace(self):
        # This add to the template namespace global variable used in
        # Zope 2 and Silva templates.  Here should be bind at the
        # correct place in the Silva view registry so you should be
        # able to use silva macro in your templates.
        view = self._silvaView()
        return {'here': view,
                'user': getSecurityManager().getUser(),
                'container': self._silvaContext.aq_inner,}


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

    @CachedProperty
    def is_preview(self):
        return IPreviewLayer.providedBy(self.request)

    @CachedProperty
    def content(self):
        if self.is_preview:
            return self.context.get_previewable()
        return self.context.get_viewable()

    def namespace(self):
        return {'content': self.content}


class ContentProvider(grok.ViewletManager):
    """A content provider in Silva. In fact it's just a viewlet
    manager...
    """

    grok.implements(IContentProvider)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace


class ViewletManager(grok.ViewletManager):
    """A viewlet manager in Silva.
    """

    grok.implements(IViewletManager)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)


class Viewlet(grok.Viewlet):
    """A viewlet in Silva
    """

    grok.implements(IViewlet)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

