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

    def url(preview=False, relative=False, host=None):
        """Return an public URL to the content, or the preview URL, or
        the url with a different host prefix.
        """

    def preview():
        """Alias url(preview=True).
        """

#BBB
ISilvaURL = IContentURL

# Adapters


class IVirtualSite(Interface):
    """Adapter on a Zope request to retrieve the root object for the
    current site. If url rewriting is used, the root object for your
    site might not be your Silva Root object, but a Silva Publication
    or a Silva Folder (where the url rewriting is done). It will be
    called the virtual root object. If a rewriting rule is used, we
    can have:

    - http://example.com is a Silva Folder at /silva/folder

    If you use different url rewriting rules inside the same site,
    it is possible that the top level url and path to the site is not
    the url and path to the root object of the site:

    - http://example.com/site is the Silva Root at /silva

    - http://example.com is a Silva Folder at /silva/folder
    """

    def get_root():
        """Return the root object of the current site, which can be
        either the virtual root object or the Silva root depending if
        url rewriting is used for the request or not.
        """

    def get_root_path():
        """Return the path to the root object. (Meaning the path
        between the start of the url and either to the Silva root or
        the virtual root).

        This is usefull to set cookies on the root of the site.
        """

    def get_root_url():
        """Return the URL of the root object of the current site.
        """

    def get_top_level_path():
        """Return the path to the top level object representing the
        site, that might be a different object than the root object if
        multiple rewrite rules are used on the site and some of them
        declare a path higher than the one declared for the root
        object.

        This is usefull to set cookies on the site.
        """

    def get_top_level_url():
        """Return the url to the top level object representing the
        site, that might be a different object than the root object if
        multiple rewrite rules are used in the site and some of them
        declare a url higher than the one declared for the root
        object.
        """

    def get_silva_root():
        """Return the Silva Root object.
        """

    def get_virtual_root():
        """Return the virtual root object defined by the current url
        rewriting rule or None if no url rewriting is done.
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


