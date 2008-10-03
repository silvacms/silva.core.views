# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component, interface

from silva.core.views import interfaces
import z3c.form.interfaces


class Adapter(object):

    def __init__(self, context):
        self.context = context


class ButtonStyle(Adapter):
    component.adapts(z3c.form.interfaces.IButton)
    interface.implements(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button'
        widget.style = u'float: right;'


class CancelButtonStyle(Adapter):
    component.adapts(interfaces.ICancelButton)
    interface.implements(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button canceler'
        widget.style = u'float: left;'


class TextInputStyle(Adapter):
    component.adapts(z3c.form.interfaces.ITextWidget)
    interface.implements(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 20


class TextAreaStyle(Adapter):
    component.adapts(z3c.form.interfaces.ITextAreaWidget)
    interface.implements(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.cols= 80
        widget.rows = 20

