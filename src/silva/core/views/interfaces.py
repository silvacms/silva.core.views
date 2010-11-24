# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from grokcore.view.interfaces import IGrokView
from grokcore.viewlet.interfaces import IViewletManager as IBaseViewletManager
from zope.contentprovider.interfaces import (
    IContentProvider as IBaseContentProvider)
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.viewlet.interfaces import IViewlet as IBaseViewlet

import zope.deferredimport
zope.deferredimport.deprecated(
    'Please import from silva.core.smi instead,'
    'this import will be removed in Silva 2.4',
    ISMIView='silva.core.smi.interfaces:ISMIView',
    ISMITab='silva.core.smi.interfaces:ISMITab',)


class ITestRequest(IBrowserRequest):
    """Marker interface to mark a TestRequest.
    """


# Preview layer

class INonCachedLayer(IBrowserRequest):
    """Layer that prevent its content to be cached by the HTTP protocol.
    """


class IPreviewLayer(INonCachedLayer):
    """This layer enable the fact to display preview version instead
    of public version.
    """

# View

class IGrokCustomizable(Interface):
    """A grok template which can be customized with a TTW template.

    Conviently it's a sub-set of a GrokView: it's need.
    """

    def update():
        """Update method which have to be called before rendering the
        template.
        """

    def default_namespace():
        """Return default namespace values.
        """


class ITemplateNotCustomizable(Interface):
    """Marker interface to put on view/template that you don't people be able
    to customize.
    """


class IView(IGrokView):
    """A view in Silva.
    """

    is_preview = Attribute(u"Boolean which say if you're in preview mode.")
    content = Attribute(u"Version of the content to render.")


class IZMIView(IGrokView):
    """A view in ZMI.
    """

class IContentProvider(IBaseContentProvider, IGrokCustomizable):
    """A customizable Content Provider.
    """


class IViewletManager(IBaseViewletManager, IGrokCustomizable):
    """A customizable Viewlet Manager.
    """


class IViewlet(IBaseViewlet, IGrokCustomizable):
    """A customizable Viewlet.
    """

class ITemplateCustomizable(IGrokCustomizable):
    """A page that you can customize.
    """

# TTW Templates

class ICustomizedTemplate(ITemplateCustomizable):
    """A through the web template.
    """

# URL management / with preview

class ISilvaURL(IAbsoluteURL):
    """Extends the absolute URL mechanism to support preview and
    public URLs.
    """

    def preview():
        """Return URL for preview.
        """

# Adapters

class IVirtualSite(Interface):
    """Adapter on a Zope request to retrieve the root object of the
    current site. If a Virtual Host Monster is used, the root object
    for your site might not be your Silva root, but a publication or a
    folder.
    """

    def get_root():
        """Return the root object of the current site, which can be
        either the virtual root object or the Silva root depending if
        Virtual Host Monster rewriting is used for the request or not.
        """

    def get_root_url():
        """Return the URL of the root object of the current site.
        """

    def get_silva_root():
        """Return the Silva root.
        """

    def get_virtual_root():
        """Return the virtual root object defined by the Virtual Host
        Monster or None if the Virtual Host Monster was not used.
        """

    def get_virtual_path():
        """Return the path (as a tuple of identifier) to the virtual
        defined by the Virtual Host Monster or None if the Virtual
        Host Monster was not used.
        """


class IHTTPResponseHeaders(Interface):
    """Adapter on a context and a request which is used to set HTTP
    headers on the response.

    Headers can be cache control settings, ...
    """

    def cache_headers():
        """ Set the cache and Last modified settings.
        """

    def other_headers(headers):
        """ Set other headers.
        """

    def __call__(**headers):
        """Set headers on the response

        method should accept **kwargs argument to override headers
        """


