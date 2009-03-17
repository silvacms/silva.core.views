# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component, interface

from silva.core.views import interfaces
import z3c.form.interfaces


class Style(object):

    interface.implements(interfaces.ISilvaStyle)

    def __init__(self, item, form):
        self.item = item
        self.form = form

    def style(self, widget):
        pass


class ButtonStyle(Style):
    component.adapts(z3c.form.interfaces.IButton,
                     interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'button'
        widget.style = u'float: right;'


class CancelButtonStyle(Style):
    component.adapts(interfaces.ICancelButton,
                     interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'button canceler'
        widget.style = u'float: left;'


class TextInputStyle(Style):
    component.adapts(z3c.form.interfaces.ITextWidget,
                     interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 20


class TextAreaStyle(Style):
    component.adapts(z3c.form.interfaces.ITextAreaWidget,
                     interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'store'
        widget.cols = 80
        widget.rows = 20

