# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from grokcore.view.interfaces import IGrokView
from grokcore.viewlet.interfaces import IViewletManager as IBaseViewletManager
from zope.contentprovider.interfaces import (
    IContentProvider as IBaseContentProvider)
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.viewlet.interfaces import IViewlet as IBaseViewlet
from silva.core.conf.martiansupport.directives import only_for
from silva.core.interfaces.content import ICustomizable, IPublishable


class IRender(Interface):
    """Interface for a IRender.
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


class IHTTPHeaderView(Interface):
    """A rendered view where HTTP headers must be set after traversal.
    """
    request = Attribute(u"Request rendered")
    context = Attribute(u"Context rendered")


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

# Customization tag


class ICustomizableTag(ICustomizable):
    """This is a tag that you can set on object to customize them.
    """


class IDisableBreadcrumbTag(ICustomizableTag):
    """Hide content from breadcrumbs
    """
    only_for(IPublishable)


class IDisableNavigationTag(ICustomizableTag):
    """Hide content from navigation
    """
    only_for(IPublishable)


# URL management / with preview

class IContentURL(IAbsoluteURL):
    """Extends the absolute URL mechanism to support preview and
    public URLs.
    """

    def url(preview=False, relative=False):
        """Return an public URL to the content.
        """

    def preview():
        """Alias url(preview=True).
        """

#BBB
ISilvaURL = IContentURL

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

    def get_root_path():
        """Return the path to the root object from the public side
        (meaning the path between the start of the url and either to
        the Silva root or virtual root).

        This is usefull to set cookies to the root of the site.
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


