# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.contentprovider.interfaces import IContentProvider \
    as IBaseContentProvider
from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewlet as IBaseViewlet
from grokcore.viewlet.interfaces import IViewletManager as IBaseViewletManager
from zope import schema

from grokcore.view.interfaces import IGrokView
from z3c.form.interfaces import IButton, ISubForm as IBaseSubForm

from silva.core.conf import schema as silvaschema

from Products.Silva.i18n import translate as _

# View

class IZMIObject(Interface):
    """ZMI Object.
    """

class IFeedback(Interface):
    """Feedback information.
    """

    status = Attribute(u"Feedback message")
    status_type = Attribute(u"Feedback type, error or feedback")



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


class IContentProvider(IBaseContentProvider):
    """A customizable Content Provider.
    """


class IViewletManager(IBaseViewletManager):
    """A customizable Viewlet Manager.
    """


class IViewlet(IBaseViewlet):
    """A customizable Viewlet.
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

    def get_root():
        """Return the virtual root of the current site.
        """

    def get_root_url():
        """
        """

    def get_silva_root():
        """
        """

    def get_virtual_root():
        """Return the virtual root or None.
        """

    def get_virtal_path():
        """Return the virtual path or None.
        """


class IHTTPResponseHeaders(Interface):
    """ Set some headers on the response from the context

    Headers can be cache control settings, ...
    """

    def cache_headers():
        """ Set the cache and Last modified settings
        """

    def other_headers(headers):
        """ Set other headers
        """

    def __call__(**headers):
        """Set headers on the response
        """
