# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.views import interfaces
import z3c.form.interfaces

class ButtonStyle(grok.Adapter):
    grok.context(z3c.form.interfaces.IButton)
    grok.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button'
        widget.style = u'float: right;'


class CancelButtonStyle(grok.Adapter):
    grok.context(interfaces.ICancelButton)
    grok.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'button canceler'
        widget.style = u'float: left;'


class TextInputStyle(grok.Adapter):
    grok.context(z3c.form.interfaces.ITextWidget)
    grok.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 20


class TextAreaStyle(grok.Adapter):
    grok.context(z3c.form.interfaces.ITextAreaWidget)
    grok.provides(interfaces.ISilvaStyle)

    def style(self, widget):
        widget.klass = u'store'
        widget.cols= 80
        widget.rows = 20

