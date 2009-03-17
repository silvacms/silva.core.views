# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.contentprovider.interfaces import IContentProvider as IBaseContentProvider
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.viewlet.interfaces import IViewlet as IBaseViewlet
from grokcore.viewlet.interfaces import IViewletManager as IBaseViewletManager
from zope import schema

from grokcore.view.interfaces import IGrokView

from silva.core.conf.fields import ID

from Products.Silva.i18n import translate as _

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

class ITemplateCustomizable(Interface):
    """This is a template used in Silva which can be customized.
    """

class ITemplate(IGrokView, ITemplateCustomizable, IGrokCustomizable):
    """A template used in Silva which can be customized.
    """

class IView(ITemplate):
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
    """Default fields used in a add form. You don't have to defines this fields.
    """

    id = ID(
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

# z3c.form Silva support

from z3c.form.interfaces import IButton

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
