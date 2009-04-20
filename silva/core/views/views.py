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
from silva.core.views.interfaces import ITemplate, IView, ILayout
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.layout.interfaces import ISMILayer
from silva.core.conf.utils import getSilvaViewFor

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

    grok.implements(IZMIView)
    grok.baseclass()
    grok.require('zope2.ViewManagementScreens')


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

    grok.implements(ISMIView)

    grok.baseclass()
    grok.context(ISilvaObject)
    grok.layer(ISMILayer)

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
        return grok.name.bind().get(self, default=default_view_name)

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


class Layout(Acquisition.Explicit):
    """A layout object.
    """

    grok.implements(ILayout)
    grok.baseclass()
    grok.context(ISilvaObject)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.view = None

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['view'] = self.view
        namespace['layout'] = self
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    @property
    def response(self):
        return self.request.response

    def _render_template(self):
        return self.template.render(self)

    def render(self):
        return self._render_template()

    render.base_method = True

    def __call__(self, view):
        self.view = view
        self.update()
        return self.render()


class Template(SilvaGrokView):
    """A view class not binded to a content.
    """

    grok.implements(ITemplate)
    grok.baseclass()
    grok.context(ISilvaObject)

    def __init__(self, context, request):
        super(Template, self).__init__(context, request)
        self.layout = None

    def default_namespace(self):
        namespace = super(Template, self).default_namespace()
        namespace['layout'] = self.layout
        return namespace

    @property
    def content(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        self.layout = zope.component.getMultiAdapter(
            (self.context, self.request), ILayout)
        return self.layout(self)


class View(SilvaGrokView):
    """View on Silva object, support view and preview
    """

    grok.implements(IView)
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.name(u'content.html')

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


class ViewletLayoutSupport(object):
    """This add layout on the object and namespace if the view is an
    ITemplate.
    """

    def __init__(self, *args):
        super(ViewletLayoutSupport, self).__init__(*args)
        self.layout = None
        if ITemplate.providedBy(self.view):
            self.layout = self.view.layout

    def default_namespace(self):
        namespace = super(ViewletLayoutSupport, self).default_namespace()
        if self.layout:
            namespace['layout'] = self.layout
        return namespace


class ViewletManager(ViewletLayoutSupport, grok.ViewletManager):
    """A viewlet manager in Silva.
    """

    grok.implements(IViewletManager)
    grok.baseclass()
    grok.context(ISilvaObject)


class ContentProvider(ViewletManager):
    """A content provider in Silva. In fact it's just a viewlet
    manager...
    """

    grok.implements(IContentProvider)
    grok.baseclass()
    grok.context(ISilvaObject)

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace


class Viewlet(ViewletLayoutSupport, grok.Viewlet):
    """A viewlet in Silva
    """

    grok.implements(IViewlet)
    grok.baseclass()
    grok.context(ISilvaObject)


