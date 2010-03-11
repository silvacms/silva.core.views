# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import schema
from zope.contentprovider.interfaces import IContentProvider \
    as IBaseContentProvider
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.viewlet.interfaces import IViewlet as IBaseViewlet

from grokcore.view.interfaces import IGrokView
from grokcore.viewlet.interfaces import IViewletManager as IBaseViewletManager
from z3c.form.interfaces import IButton, ISubForm as IBaseSubForm

from silva.core.conf import schema as silvaschema
from silva.translations import translate as _


class ITestRequest(IBrowserRequest):
    """Marker interface to mark a TestRequest.
    """


# Preview layer

class IPreviewLayer(IBrowserRequest):
    """This layer enable the fact to display preview version instead
    of public version.
    """

# View

class IFeedback(Interface):
    """Feedback information.
    """

    status = Attribute(u"Feedback message")
    status_type = Attribute(u"Feedback type, error or feedback")


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


class ISMIView(IGrokView):
    """A view in SMI.
    """

    tab_name = Attribute("Name of the current tab.")
    active_tab = Attribute(u"Which is the current active tab")
    vein = Attribute(u"What's the vein to display")

class ISMITab(ISMIView):
    """A tab in SMI.
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

    def preview():
        """Return URL for preview.
        """

# Silva forms

class IDefaultAddFields(Interface):
    """Default fields used in a add form. You don't have to defines
    this fields.
    """

    id = silvaschema.ID(
        title=_(u"id"),
        description=_(u"No spaces or special characters besides ‘_’ or ‘-’ or ‘.’"),
        required=True)
    title = schema.TextLine(
        title=_(u"title"),
        description=_(u"The title will be publicly visible, and is used for the link in indexes."),
        required=True)


class ISilvaForm(Interface):
    """A Silva form.
    """


class ISilvaFormlibForm(ISilvaForm):
    """A Silva form built using formlib.
    """


class ISilvaStyledForm(Interface):
    """A form with a Silva style.
    """


class ISilvaZ3CFormForm(ISilvaForm, ISilvaStyledForm):
    """A Silva form built using z3c.form.
    """


class ISubForm(IBaseSubForm):
    """A Silva subform.
    """

# z3c.form Silva support

class ICancelButton(IButton):
    """A button to cancel a form.
    """


class INoCancelButton(Interface):
    """Marker interface for Z3CForm to say that you don't want a
    cancel button.
    """


class ISilvaStyle(Interface):
    """Adapter used to apply new style information on z3c.form
    elements.
    """

    def style(widget):
        """Apply Silva style to that element.
        """

# Adapters

class IVirtualSite(Interface):
    """This adapts the request and let you access the root object of
    the current site. If Virtual Host Monster, the root object for
    your might not be your Silva root.
    """

    def get_root():
        """Return the root of the current site, which will be either
        the virtual root or the Silva if Virtual Host Monster
        rewriting is used for the request, and where.
        """

    def get_root_url():
        """Return the URL of the root of the current site.
        """

    def get_silva_root():
        """Return the Silva root.
        """

    def get_virtual_root():
        """Return the virtual root defined by the Virtual Host Monster
        or None.
        """

    def get_virtual_path():
        """Return the path to the virtual defined by the Virtual Host
        Monster or None.
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
