# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.contentprovider.interfaces import IContentProvider
from zope.i18n import translate
from zope.security.interfaces import IPermission
from zope.viewlet.interfaces import IViewletManager, IViewlet
from zope import component, interface
import zope.cachedescriptors.property

from five import grok
import urllib

from Products.Silva.interfaces import ISilvaObject
from Products.Five.viewlet.manager import ViewletManagerBase
from Products.Five.viewlet.viewlet import ViewletBase

from silva.core.views.interfaces import IFeedback, IZMIView, ISMIView
from silva.core.views.interfaces import ITemplate, IPreviewLayer, IView
from silva.core.conf.utils import getSilvaViewFor
from silva.core import conf as silvaconf

from AccessControl import getSecurityManager
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
        return super(SilvaGrokView, self).publishTraverse(request, name)

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


class SMIView(SilvaGrokView):
    """A view in SMI.
    """

    grok.implements(ISMIView)

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

    def __init__(self, context, request):
        super(SMIView, self).__init__(context, request)

        # Set model on request like SilvaViews
        self.request['model'] = context
        # Set id on template some macros uses template/id
        self.template._template.id = self.__view_name__


    def _silvaView(self):
        # Lookup the correct Silva edit view so forms are able to use
        # silva macros.
        return getSilvaViewFor(self.context, 'edit', self.context)

    def namespace(self):
        # This add to the template namespace global variable used in
        # Zope 2 and Silva templates.  Here should be bind at the
        # correct place in the Silva view registry so you should be
        # able to use silva macro in your templates.
        view = self._silvaView()
        return {'here': view,
                'realview': self, # XXX should be removed when silva
                                  # stop to do stupid things with view
                                  # in templates.
                'user': getSecurityManager().getUser(),
                'container': self.context.aq_inner,}


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


class ContentProviderBase(Acquisition.Explicit):

    silvaconf.baseclass()
    silvaconf.context(ISilvaObject)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        static = component.queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)
        if not (static is None):
            self.static = static.__of__(self)
        else:
            self.static = static
        self.__parent__ = view
        self.__name__ = self.__view_name__

    getPhysicalPath = Acquisition.Acquired

    def namespace(self):
        return {}

    def default_namespace(self):
        namespace = {}
        namespace['view'] = self.view
        namespace['static'] = self.static
        return namespace


class ContentProvider(ContentProviderBase):

    grok.implements(IContentProvider)

    silvaconf.baseclass()

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace

    def update(self):
        pass

    def render(self):
        return self.template.render(self)

class ViewletManager(ContentProviderBase, ViewletManagerBase):

    grok.implements(IViewletManager)

    silvaconf.baseclass()

    def __init__(self, context, request, view):
        ContentProviderBase.__init__(self, context, request, view)
        ViewletManagerBase.__init__(self, context, request, view)

    def sort(self, viewlets):
        s_viewlets = []
        for name, viewlet in viewlets:
             viewlet.__viewlet_name__ = name
             s_viewlets.append(viewlet)

        def sort_key(viewlet):
            # If components have a grok.order directive, sort by that.
            explicit_order, implicit_order = silvaconf.order.bind().get(viewlet)
            return (explicit_order,
                    viewlet.__module__,
                    implicit_order,
                    viewlet.__class__.__name__)
        s_viewlets = sorted(s_viewlets, key=sort_key)
        return [(viewlet.__viewlet_name__, viewlet) for viewlet in s_viewlets]

    def filter(self, viewlets):
        # Wrap viewlet in aquisition, and only return viewlets
        # accessible to the user.
        parent = self.aq_parent
        security_manager = getSecurityManager()

        def checkPermission(viewlet):
            _, viewlet = viewlet
            # Unfortuanetly, we don't have easy way to check the permission.
            permission = silvaconf.require.bind().get(viewlet)
            if (permission is None) or (permission == 'zope.Public'):
                return True
            if isinstance(permission, str):
                permission = component.getUtility(IPermission, permission)
            return security_manager.checkPermission(permission.title, viewlet)

        return filter(checkPermission,
                      [(name, viewlet.__of__(parent)) for name, viewlet in viewlets])

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['viewletmanager'] = self
        return namespace



class Viewlet(ContentProviderBase, ViewletBase):

    grok.implements(IViewlet)

    silvaconf.baseclass()

    def __init__(self, context, request, view, viewletmanager):
        ContentProviderBase.__init__(self, context, request, view)
        self.viewletmanager = viewletmanager

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['viewlet'] = self
        namespace['viewletmanager'] = self.viewletmanager
        return namespace

    def update(self):
        pass

    def render(self):
        return self.template.render(self)


from five.resourceinclude.provider import ResourceIncludeProvider

class ResourceContentProvider(ResourceIncludeProvider, ContentProvider):

    silvaconf.name('resources')
