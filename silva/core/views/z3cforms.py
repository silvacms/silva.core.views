# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface, component

from Products.Silva.i18n import translate as _
from Products.Silva.ViewCode import ViewCode

from silva.core.views.interfaces import ISilvaZ3CFormForm, IDefaultAddFields, \
    ICancelButton, ISilvaStyle, INoCancelButton, ISilvaStyledForm
from silva.core.views.views import SMIView
from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, \
    SilvaMixinEditForm
from silva.core import conf as silvaconf
from silva.core.interfaces import IVersionedContent
from silva.core.conf import schema as silvaschema
import grokcore.view
from five import grok

from five.megrok.z3cform.components import GrokForm
from z3c.form import form, button, field
from plone.z3cform.crud import crud
from plone.z3cform import converter
import z3c.form.interfaces

# Base class to grok forms

class SilvaGrokForm(SilvaMixinForm, GrokForm, ViewCode):
    """Silva Gork form for z3cform.
    """

    interface.implements(ISilvaZ3CFormForm)
    silvaconf.baseclass()

    @apply
    def status_type():
        def get(self):
            if self._status_type:
                return self._status_type
            if hasattr(self, 'formErrorsMessage'):
                if self.formErrorsMessage == self.status:
                    return 'error'
            return 'feedback'
        def set(self, type):
            self._status_type = type
        return property(get, set)


class PageForm(SilvaGrokForm, form.Form, SMIView):
    """Generic form.
    """

    silvaconf.baseclass()


class AddForm(SilvaMixinAddForm, SilvaGrokForm, form.AddForm, SMIView):
    """Add form.
    """

    interface.implements(component.IFactory)
    silvaconf.baseclass()
    form.extends(form.AddForm, ignoreButtons=True, ignoreHandlers=True)

    def updateForm(self):
        field_to_add = field.Fields()
        for name in IDefaultAddFields:
            if self.fields.get(name) is None:
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


class EditForm(SilvaMixinEditForm, SilvaGrokForm, form.EditForm, SMIView):
    """Edit form.
    """

    silvaconf.baseclass()
    silvaconf.name(u"tab_edit")
    form.extends(form.AddForm, ignoreButtons=True, ignoreHandlers=True)

    def updateForm(self):
        editable_obj =  self.context.get_editable()
        if editable_obj is None:
            self.versioned_content = IVersionedContent.providedBy(self.context)
            self.propose_new_version = self.versioned_content
            self.is_editable = False
        else:
            super(EditForm, self).updateForm()

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

class SilvaGrokSubForm(SilvaGrokForm):

    silvaconf.baseclass()

    @apply
    def status():
        def get(self):
            return self.context.status
        def set(self, status):
            self.context.status = status
        return property(get, set)


class CrudAddForm(SilvaGrokSubForm, crud.AddForm, SMIView):
    """The add form of a CRUD form.
    """

    interface.implements(INoCancelButton)

    template = grokcore.view.PageTemplateFile('templates/z3cform.pt')
    ignoreRequest = False

    @property
    def label(self):
        return _(u"add ${label}", mapping=dict(label=self.context.label))


class CrudEditSubForm(crud.EditSubForm):
    """An crud edit sub-form.
    """

    interface.implements(ISilvaStyledForm)


class CrudEditForm(SilvaGrokSubForm, crud.EditForm, SMIView):
    """The edit form of a CRUD form.
    """

    interface.implements(INoCancelButton)

    editsubform_factory = CrudEditSubForm
    template = grokcore.view.PageTemplateFile('templates/crud_editform.pt')

    @property
    def label(self):
        return _(u"modify ${label}", mapping=dict(label=self.context.label))


class CrudForm(SilvaGrokForm, crud.CrudForm, SMIView):
    """Crud form.
    """

    interface.implements(INoCancelButton)

    template = grokcore.view.PageTemplateFile('templates/crud_form.pt')
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

@silvaconf.subscribe(z3c.form.interfaces.IAfterWidgetUpdateEvent)
def customizeWidgets(event):
    item = widget = event.widget
    form = widget.form
    if z3c.form.interfaces.IAction.providedBy(widget):
        item = widget.field
    apply_style = component.queryMultiAdapter((item, form), ISilvaStyle)
    if apply_style:
        apply_style.style(widget)


# Cancel button on every forms

class CancelButton(button.Button):
    """A cancel button.
    """

    interface.implements(ICancelButton)


class SilvaFormActions(button.ButtonActions, grok.MultiAdapter):
    grok.adapts(ISilvaZ3CFormForm,
                interface.Interface,
                interface.Interface)

    def update(self):
        if not INoCancelButton.providedBy(self.form):
            self.form.buttons = button.Buttons(
                self.form.buttons,
                CancelButton('cancel', _(u'cancel'), accessKey=u'c'))
        super(SilvaFormActions, self).update()



class SilvaAddActionHandler(button.ButtonActionHandler, grok.MultiAdapter):
    grok.adapts(ISilvaZ3CFormForm,
                interface.Interface,
                interface.Interface,
                button.ButtonAction)

    def __call__(self):
        if not INoCancelButton.providedBy(self.form):
            if self.action.name == 'form.buttons.cancel':
                self.form.redirect('%s/edit' % self.form.context.absolute_url())
                return
        super(SilvaAddActionHandler, self).__call__()


class FileUploadDataConverter(
    converter.FileUploadDataConverter, grok.MultiAdapter):
    grok.adapts(silvaschema.IBytes,
                z3c.form.interfaces.IFileWidget)

    def toFieldValue(self, value):
        return value

    def toWidgetValue(self, value):
        return super(FileUploadDataConverter, self).toFieldValue(value)
