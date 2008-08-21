# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface
from zope import schema

from grokcore.view.interfaces import IGrokView

from silva.core.conf.fields import ID

from Products.Silva.i18n import translate as _


class IFeedbackView(interface.Interface):

    status = interface.Attribute(u"Feedback message")
    status_type = interface.Attribute(u"Feedback type, error or feedback")


# Silva forms


class IDefaultAddFields(interface.Interface):
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



class ISilvaView(IGrokView):
    """A view in Silva.
    """

class IZMIView(IGrokView):
    """A view in ZMI.
    """

class ISilvaForm(interface.Interface):
    """A Silva form.
    """

class ISilvaFormlibForm(ISilvaForm):
    """A Silva form built using formlib.
    """

class ISilvaZ3CFormForm(ISilvaForm):
    """A Silva form built using z3c.form.
    """

class ISilvaViewNotCustomizable(Interface):
    """Marker interface to put on view that you don't people be able
    to customize.
    """

# z3c.form Silva support

import z3c.form.interfaces

class ICancelButton(z3c.form.interfaces.IButton):
    """A button to cancel a form.
    """

class ISilvaStyle(interface.Interface):
    """Adapter used to apply new style information on z3c.form
    elements.
    """

    def style(widget):
        """Apply Silva style to that element.
        """
