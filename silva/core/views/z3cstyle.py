# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.views import interfaces
import z3c.form.interfaces


class Style(grok.MultiAdapter):
    grok.baseclass()
    grok.implements(interfaces.ISilvaStyle)

    def __init__(self, item, form):
        self.item = item
        self.form = form

    def style(self, widget):
        pass


class ButtonStyle(Style):
    grok.adapts(z3c.form.interfaces.IButton,
                interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'button'
        widget.style = u'float: right;'


class CancelButtonStyle(Style):
    grok.adapts(interfaces.ICancelButton,
                interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'button canceler'
        widget.style = u'float: left;'


class TextInputStyle(Style):
    grok.adapts(z3c.form.interfaces.ITextWidget,
                interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 20


class FileUploadStyle(Style):
    grok.adapts(z3c.form.interfaces.IFileWidget,
                interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'store'
        widget.size = 54


class TextAreaStyle(Style):
    grok.adapts(z3c.form.interfaces.ITextAreaWidget,
                interfaces.ISilvaStyledForm)

    def style(self, widget):
        widget.klass = u'store'
        widget.cols = 80
        widget.rows = 20

