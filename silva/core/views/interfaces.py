# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.contentprovider.interfaces import IContentProvider as IBaseContentProvider
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.viewlet.interfaces import IViewlet as IBaseViewlet
from zope import schema

from grokcore.view.interfaces import IGrokView

from silva.core.conf.fields import ID

from Products.Silva.i18n import translate as _


# View

class IFeedback(Interface):
    """Feedback information.
    """

    status = Attribute(u"Feedback message")
    status_type = Attribute(u"Feedback type, error or feedback")


class ITTWCustomizable(Interface):
    """Can be customized with a TTW template.
    """

    def update():
        """Update method which have to be called before rendering the
        template.
        """

class ITemplate(IGrokView, ITTWCustomizable):
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

class ITemplateNotCustomizable(Interface):
    """Marker interface to put on view/template that you don't people be able
    to customize.
    """

class IContentProvider(IBaseContentProvider, ITTWCustomizable):
    """A customizable Content Provider.
    """

class IViewlet(IBaseViewlet, ITTWCustomizable):
    """A customizable Viewlet.
    """

# TTW Templates

class ICustomizedTemplate(Interface):
    """A through the web template.
    """

# Preview layer

class IPreviewLayer(IBrowserRequest):
    """This layer enable the fact to display preview version instead
    of public version.
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

class ISilvaZ3CFormForm(ISilvaForm):
    """A Silva form built using z3c.form.
    """

# z3c.form Silva support

from z3c.form.interfaces import IButton

class ICancelButton(IButton):
    """A button to cancel a form.
    """

class ISilvaStyle(Interface):
    """Adapter used to apply new style information on z3c.form
    elements.
    """

    def style(widget):
        """Apply Silva style to that element.
        """
