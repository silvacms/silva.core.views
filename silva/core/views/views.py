# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.i18n import translate
from zope.interface import implements
from zope.security.interfaces import IPermission
from zope.viewlet.interfaces import IViewletManager
from zope import component, interface
import zope.cachedescriptors.property

import urllib

from Products.Silva.interfaces import ISilvaObject
from Products.Five.viewlet.manager import ViewletManagerBase
from Products.Five.viewlet.viewlet import ViewletBase
from Products.Five import BrowserView

from silva.core.views.interfaces import IFeedback, ISMIView
from silva.core.views.interfaces import ITemplate, IView
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.conf.utils import getSilvaViewFor

from AccessControl import getSecurityManager
import Acquisition

# Simple views

class SilvaBaseView(BrowserView):
    """Grok View on Silva objects.
    """

    @property
    def response(self):
        return self.request.RESPONSE

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
                super(SilvaBaseView, self).redirect(url + join_char + to_append)
                return
        self.response.redirect(url)

    def namespace(self):
        return {}

    def default_namespace(self):
        return {}


class SMIView(SilvaBaseView):
    """A view in SMI.
    """

    implements(ISMIView)

    vein = 'contents'
    tab_name = 'tab_edit'
    active_tab = 'tab_edit'

    def __init__(self, context, request):
        super(SMIView, self).__init__(context, request)

        # Set model on request like SilvaViews
        self.request['model'] = context

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
                'container': self.context.aq_inner,}


class Template(SilvaBaseView):
    """A view class not binded to a content.
    """

    implements(ITemplate)


class View(Template):
    """View on Silva object, support view and preview
    """

    implements(IView)

    @zope.cachedescriptors.property.CachedProperty
    def is_preview(self):
        # XXX to fix
        return False

    @zope.cachedescriptors.property.CachedProperty
    def content(self):
        if self.is_preview:
            return self.context.get_previewable()
        return self.context.get_viewable()

    def namespace(self):
        return {'content': self.content}


class ContentProviderBase(Acquisition.Explicit):

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view
        self.__name__ = self.__view_name__

    def namespace(self):
        return {}

    def default_namespace(self):
        namespace = {}
        namespace['view'] = self.view
        namespace['static'] = self.static
        return namespace


class ContentProvider(ContentProviderBase):

    implements(IContentProvider)

    def default_namespace(self):
        namespace = super(ContentProvider, self).default_namespace()
        namespace['provider'] = self
        return namespace

    def update(self):
        pass

    def render(self):
        return self.template.render(self)

class ViewletManager(ContentProviderBase, ViewletManagerBase):

    implements(IViewletManager)

    def __init__(self, context, request, view):
        ContentProviderBase.__init__(self, context, request, view)
        ViewletManagerBase.__init__(self, context, request, view)

    def sort(self, viewlets):
        s_viewlets = []
        for name, viewlet in viewlets:
             viewlet.__viewlet_name__ = name
             s_viewlets.append(viewlet)

        def sort_key(viewlet):
            return (viewlet.__module__,
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

    implements(IViewlet)

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

