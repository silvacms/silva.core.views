# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface, component
from zope.pagetemplate.interfaces import IPageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.Silva.i18n import translate as _
from Products.Silva.ViewCode import ViewCode

from silva.core.views.interfaces import ISilvaZ3CFormForm, IDefaultAddFields
from silva.core.views.interfaces import ICancelButton, ISilvaStyle, INoCancelButton
from silva.core.views.views import SMIView
from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, SilvaMixinEditForm

from z3c.form import form, button, field
from z3c.form.interfaces import IFormLayer, IAction
from z3c.form.field import Fields
from plone.z3cform import z2
from plone.z3cform.crud import crud

# Base class to forms


class SilvaBaseForm(SilvaMixinForm, ViewCode):
    """Silva Grok form for z3cform.
    """

    __allow_access_to_unprotected_subobjects__ = True

    interface.implements(ISilvaZ3CFormForm)

    @property
    def status_type(self):
        if self._status_type:
            return self._status_type
        if hasattr(self, 'formErrorsMessage'):
            if self.formErrorsMessage == self.status:
                return 'error'
        return 'feedback'

    def render(self):
        # Render content template.

        if self.template is None:
            template = component.getMultiAdapter((self, self.request),
                IPageTemplate)
            return template(self)
        namespace = self.default_namespace()
        namespace.update(self.namespace())
        return self.template.__of__(self)._exec(namespace, [], {})

    def __call__(self):
        """Render the form, patching the request first with
        plone.z3cform helper.
        """
        z2.switch_on(self, request_layer=IFormLayer)
        return super(SilvaBaseForm, self).__call__()


class SilvaBaseSubForm(SilvaBaseForm):
    """Silva base subform for z3cform.
    """

    @apply
    def status():
        def get(self):
            return self.context.status
        def set(self, status):
            self.context.status = status
        return property(get, set)


class PageForm(SilvaBaseForm, form.Form, SMIView):
    """Generic form.
    """


class AddForm(SilvaMixinAddForm, SilvaBaseForm, form.AddForm, SMIView):
    """Add form.
    """

    interface.implements(component.IFactory)
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


class EditForm(SilvaMixinEditForm, SilvaBaseForm, form.EditForm, SMIView):
    """Edit form.
    """

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


class CrudAddForm(SilvaBaseSubForm, crud.AddForm, SMIView):
    """The add form of a CRUD form.
    """

    interface.implements(INoCancelButton)

    template = ViewPageTemplateFile('templates/z3cform.pt')
    ignoreRequest = False

    @property
    def label(self):
        return _(u"add ${label}", mapping=dict(label=self.context.label))


class CrudEditForm(SilvaBaseSubForm, crud.EditForm, SMIView):
    """The edit form of a CRUD form.
    """

    interface.implements(INoCancelButton)

    template = ViewPageTemplateFile('templates/crud_editform.pt')

    @property
    def label(self):
        return _(u"modify ${label}", mapping=dict(label=self.context.label))


class CrudForm(SilvaBaseForm, crud.CrudForm, SMIView):
    """Crud form.
    """

    interface.implements(INoCancelButton)

    template = ViewPageTemplateFile('templates/crud_form.pt')
    addform_factory = CrudAddForm
    editform_factory = CrudEditForm

    def update(self):
        form.Form.update(self)

        addform = self.addform_factory(self, self.request)
        editform = self.editform_factory(self, self.request)
        addform.update()
        editform.update()
        self.subforms = [addform, editform]


# Macros to render z3c forms

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Z3CFormMacros(BrowserView):
    template = ViewPageTemplateFile('templates/z3cform.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

# Customization of widgets

def customizeWidgets(event):
    item = widget = event.widget
    if IAction.providedBy(widget):
            item = widget.field
    apply_style = component.queryAdapter(item, ISilvaStyle)
    if apply_style:
        apply_style.style(widget)


# Cancel button on every forms

class CancelButton(button.Button):
    """A cancel button.
    """

    interface.implements(ICancelButton)


class SilvaFormActions(button.ButtonActions):
    component.adapts(ISilvaZ3CFormForm,
                     interface.Interface,
                     interface.Interface)

    def update(self):
        if not INoCancelButton.providedBy(self.form):
            self.form.buttons = button.Buttons(
                self.form.buttons,
                CancelButton('cancel', _(u'cancel'), accessKey=u'c'))
        super(SilvaFormActions, self).update()


class SilvaAddActionHandler(button.ButtonActionHandler):
    component.adapts(ISilvaZ3CFormForm,
                     interface.Interface,
                     interface.Interface,
                     button.ButtonAction)

    def __call__(self):
        if not INoCancelButton.providedBy(self.form):
            if self.action.name == 'form.buttons.cancel':
                self.form.redirect('%s/edit' % self.form.context.absolute_url())
                return
        super(SilvaAddActionHandler, self).__call__()
