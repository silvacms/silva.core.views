# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from grokcore import component

from silva.core.views import interfaces
import z3c.form.interfaces

class ButtonStyle(component.Adapter):
    component.context(z3c.form.interfaces.IButton)
    component.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button'
        widget.style = u'float: right;'


class CancelButtonStyle(component.Adapter):
    component.context(interfaces.ICancelButton)
    component.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button canceler'
        widget.style = u'float: left;'


class TextInputStyle(component.Adapter):
    component.context(z3c.form.interfaces.ITextWidget)
    component.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 20


class TextAreaStyle(component.Adapter):
    component.context(z3c.form.interfaces.ITextAreaWidget)
    component.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.cols= 80
        widget.rows = 20

