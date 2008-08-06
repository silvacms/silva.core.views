# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface
from zope.component import queryAdapter
from grokcore import component

from Products.Silva.i18n import translate as _
from Products.Silva.ViewCode import ViewCode

from silva.core.views.interfaces import ISilvaZ3CFormForm, IDefaultAddFields
from silva.core.views.interfaces import ICancelButton, ISilvaStyle
from silva.core.views.views import SilvaGrokView
from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, SilvaMixinEditForm
from silva.core import conf as silvaconf

from plone.z3cform.components import GrokForm
from z3c.form.interfaces import IFormLayer, IAction, IWidget
from z3c.form import form, button, field


# Base class to grok forms

class SilvaGrokForm(SilvaMixinForm, GrokForm, ViewCode):
    """Silva Gork form for z3cform.
    """

    interface.implements(ISilvaZ3CFormForm)
    silvaconf.baseclass()

    def updateWidgets(self):
        super(SilvaGrokForm, self).updateWidgets()
        for widget in self.widgets.values():
            apply_style = queryAdapter(widget, ISilvaStyle)
            if apply_style:
                apply_style.style(widget)

    def updateActions(self):
        super(SilvaGrokForm, self).updateActions()
        for action in self.actions.values():
            apply_style = queryAdapter(action.field, ISilvaStyle)
            if apply_style:
                apply_style.style(action)

    @property
    def status_type(self):
        if self._status_type:
            return self._status_type
        if hasattr(self, 'formErrorsMessage'):
            if self.formErrorsMessage == self.status:
                return 'error'
        return 'feedback'


class PageForm(SilvaGrokForm, form.Form, SilvaGrokView):
    """Generic form.
    """

    silvaconf.baseclass()
    

class AddForm(SilvaMixinAddForm, SilvaGrokForm, form.AddForm, SilvaGrokView):
    """Add form.
    """

    silvaconf.baseclass()
    form.extends(form.AddForm, ignoreButtons=True, ignoreHandlers=True)

    def updateForm(self):
        field_to_add = field.Fields()
        for name in IDefaultAddFields:
            if self.fields.get(field) is None:
                field_to_add += field.Fields(IDefaultAddFields[name])
        if field_to_add:
            self.fields = field_to_add + self.fields
        # Setup widgets
        super(AddForm, self).updateForm()

    @button.buttonAndHandler(_('save + edit'), name='save_and_edit')
    def handleSaveAndEdit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            self.redirect('%s/edit' % obj.absolute_url())

    @button.buttonAndHandler(_('save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            self.redirect('%s/edit' % self.context.absolute_url())


class EditForm(SilvaMixinEditForm, SilvaGrokForm, form.EditForm, SilvaGrokView):
    """Edit form.
    """

    silvaconf.baseclass()
    silvaconf.name(u"tab_edit")
    form.extends(form.AddForm, ignoreButtons=True, ignoreHandlers=True)

    def getContent(self):
        # Return the content to edit.
        return self.context.get_editable()


    @button.buttonAndHandler(_('save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = _(u'${meta_type} changed.',
                            mapping={'meta_type': self.context.meta_type,})
        else:
            self.status = _(u'No changes')


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


# Cancel button on every forms

class CancelButton(button.Button):
    """A cancel button.
    """

    interface.implements(ICancelButton)
    

class SilvaFormActions(button.ButtonActions, component.MultiAdapter):
    component.adapts(ISilvaZ3CFormForm,
                     interface.Interface,
                     interface.Interface)
                      
    def update(self):
        self.form.buttons = button.Buttons(
            self.form.buttons,
            CancelButton('cancel', _(u'cancel'), accessKey=u'c'))
        super(SilvaFormActions, self).update()



class SilvaAddActionHandler(button.ButtonActionHandler, component.MultiAdapter):
    component.adapts(ISilvaZ3CFormForm,
                     interface.Interface,
                     interface.Interface,
                     button.ButtonAction)

    def __call__(self):
        if self.action.name == 'form.buttons.cancel':
            self.form.redirect('%s/edit' % self.form.context.absolute_url())
            return
        super(SilvaAddActionHandler, self).__call__()
