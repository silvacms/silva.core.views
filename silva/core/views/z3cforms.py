# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface
from zope.component import provideAdapter
from grokcore import component

from Products.Silva.ViewCode import ViewCode

from silva.core.views.interfaces import ISilvaZ3CFormForm
from silva.core.views.views import SilvaGrokView
from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, SilvaMixinEditForm
from silva.core import conf as silvaconf

from plone.z3cform.components import GrokForm
from z3c.form.interfaces import IFormLayer
from z3c.form import form, button


# Base class to grok forms

class SilvaGrokForm(SilvaMixinForm, GrokForm, ViewCode):
    """Silva Gork form for z3cform.
    """

    interface.implements(ISilvaZ3CFormForm)
    silvaconf.baseclass()

class PageForm(SilvaGrokForm, form.Form, SilvaGrokView):
    """Generic form.
    """

    silvaconf.baseclass()
    

class EditForm(SilvaMixinEditForm, SilvaGrokForm, form.EditForm, SilvaGrokView):
    """Edit form.
    """

    silvaconf.baseclass()
    silvaconf.name(u"tab_edit")

    def getContent(self):
        # Return the content to edit.
        return self.context.get_editable()


class AddForm(SilvaMixinAddForm, SilvaGrokForm, form.AddForm, SilvaGrokView):
    """Add form.
    """

    silvaconf.baseclass()


# Macros to render z3c forms

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Z3CFormMacros(BrowserView):
    template = ViewPageTemplateFile('templates/z3cform.pt')
    
    def __getitem__(self, key):
        if not IFormLayer.providedBy(self.request):
            # XXX the request forgets its layer. maybe it's due to silvalayout
            interface.alsoProvides(self.request, IFormLayer)
        return self.template.macros[key]


# Cancel button

class SilvaFormActions(button.ButtonActions):
     component.adapts(ISilvaZ3CFormForm,
                      interface.Interface,
                      interface.Interface)
                      
     def update(self):
         self.form.buttons = button.Buttons(
             self.form.buttons,
             button.Button('cancel', u'Cancel'))
         super(SilvaFormActions, self).update()


provideAdapter(SilvaFormActions)
