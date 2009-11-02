# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface, component, event, schema, lifecycleevent

from Products.Silva.i18n import translate as _
from Products.Silva.ViewCode import ViewCode
from ZODB.POSException import ConflictError

from silva.core.views.interfaces import ISilvaZ3CFormForm, IDefaultAddFields, \
    ICancelButton, ISilvaStyle, INoCancelButton, ISilvaStyledForm, ISubForm
from silva.core.views.views import SMIView
from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, \
    SilvaMixinEditForm
from Products.Silva.interfaces import IVersionedContent

from silva.core.conf import schema as silvaschema

import grokcore.view
import grokcore.viewlet.util
from grokcore.view.meta.views import default_view_name
from five import grok

from zope.traversing.browser import absoluteURL

from five.megrok.z3cform.components import GrokForm
from z3c.form import form, button, field, widget
from plone.z3cform import converter
from plone.z3cform.widget import singlecheckboxwidget_factory
from z3c.form.interfaces import DISPLAY_MODE, INPUT_MODE, NOVALUE
import z3c.form.interfaces
import z3c.form.converter

# Base class to grok forms

class SilvaGrokForm(SilvaMixinForm, GrokForm, ViewCode):
    """Silva Gork form for z3cform.
    """

    grok.implements(ISilvaZ3CFormForm)
    grok.baseclass()

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

    def updateData(self):
        self.updateWidgets()

    def updateActions(self):
        super(SilvaGrokForm, self).updateActions()
        self.actions.execute()

    def updateForm(self):
        # Split the form update in two step: data and actions
        self.updateData()
        self.updateActions()

    def refreshData(self):
        # Nothing else works.
        self.updateWidgets()

    def refreshActions(self):
        # To refresh actions, you update them again.
        super(SilvaGrokForm, self).updateActions()

    def refreshForm(self):
        self.refreshData()
        self.refreshActions()


class PageForm(SilvaGrokForm, form.Form, SMIView):
    """Generic form.
    """

    grok.baseclass()


class PublicForm(GrokForm, form.Form):
    """Generic form for the public interface.
    """

    grok.implements(ISilvaZ3CFormForm)
    grok.baseclass()
    template = grok.PageTemplateFile('templates/public_form.pt')

    @property
    def form_macros(self):
        return component.queryMultiAdapter(
            (self, self.request,), name='form-macros')


class AddForm(SilvaMixinAddForm, SilvaGrokForm, form.AddForm, SMIView):
    """Add form.
    """

    grok.implements(component.IFactory)
    grok.baseclass()
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

    grok.baseclass()
    grok.name(u"tab_edit")
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
            self.status_type = 'error'
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = _(u'${meta_type} changed.',
                            mapping={'meta_type': self.context.meta_type,})
        else:
            self.status = _(u'No changes')


class ComposedForm(PageForm):
    """A more generic form which can be composed of many others.
    """

    grok.implements(INoCancelButton)
    grok.baseclass()

    template = grok.PageTemplateFile('templates/composed_form.pt')

    def updateSubForms(self):
        subforms = map(lambda x: x[1], component.getAdapters(
                (self.context, self.request,  self), ISubForm))
        subforms = grokcore.viewlet.util.sort_components(subforms)
        self.subforms = []
        # Update form
        for subform in subforms:
            if not subform.available():
                continue
            subform.update()
            subform.updateForm()
            self.subforms.append(subform)

        # Refresh values
        for subform in self.subforms:
            subform.refreshForm()

    def updateForm(self):
        self.updateSubForms()
        super(PageForm, self).updateForm()


class SubForm(PageForm):
    """A form going in a composed form.
    """

    grok.implements(INoCancelButton, ISubForm)
    grok.baseclass()

    template = grok.PageTemplateFile('templates/z3cform.pt')

    def __init__(self, context, request, parentForm):
        self.parentForm = self.__parent__ = parentForm
        super(PageForm, self).__init__(context, request)

    def available(self):
        return self.getContent() is not None

    @property
    def prefix(self):
        name = grok.name.bind().get(self) or default_view_name(self)
        return str('%s' % name)

    @apply
    def status():
        def get(self):
            return self.parentForm.status
        def set(self, status):
            self.parentForm.status = status
        return property(get, set)

    @apply
    def status_type():
        def get(self):
            return self.parentForm.status_type
        def set(self, status_type):
            self.parentForm.status_type = status_type
        return property(get, set)


class SubEditForm(SubForm, form.EditForm):
    """A subform which edit the content.
    """

    grok.baseclass()

    @button.buttonAndHandler(_('save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.status_type = 'error'
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = _(u'${meta_type} changed.',
                            mapping={'meta_type': self.context.meta_type,})
        else:
            self.status = _(u'No changes')


class CrudForm(ComposedForm):
    """A Crud form is a special composed form.
    """

    grok.baseclass()

    add_fields = field.Fields()
    update_fields = field.Fields()
    view_fields = field.Fields()

    def link(self, name, value):
        return None

    def add(self, **data):
        raise NotImplementedError

    def remove(self, data):
        raise NotImplementedError

    def getItems(self):
        raise NotImplementedError


class CrudAddForm(SubForm):
    """The add form of a CRUD form.
    """

    grok.order(20)
    grok.view(CrudForm)
    grok.name('crudaddform')

    ignoreContext = True

    def available(self):
        return self.parentForm.getContent() is not None

    @property
    def label(self):
        return _(u"add ${label}", mapping=dict(label=self.parentForm.label))

    @property
    def fields(self):
        return field.Fields(self.parentForm.add_fields)

    @button.buttonAndHandler(_('add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = form.AddForm.formErrorsMessage
            self.status_type = 'error'
            return
        try:
            item = self.parentForm.add(**data)
        except schema.ValidationError, e:
            self.status = e
        else:
            event.notify(lifecycleevent.ObjectCreatedEvent(item))
            self.ignoreRequest = True
            self.status = _(u"Item added successfully.")


class CrudEditForm(SubForm):
    """The edit form of a CRUD form.
    """

    grok.order(10)
    grok.view(CrudForm)
    grok.name('crudeditform')
    template = grok.PageTemplateFile('templates/crud_editform.pt')

    def available(self):
        return bool(self.parentForm.getItems())

    @property
    def label(self):
        return _(u"modify ${label}", mapping=dict(label=self.parentForm.label))

    def selectedItems(self):
        tuples = []
        for subform in self.subforms:
            data = subform.widgets['select'].extract()
            if not data or data is NOVALUE:
                continue
            else:
                tuples.append((subform.contentId, subform.content))
        return tuples

    def refreshData(self):
        self.updateSubForms()
        super(SubForm, self).refreshData()

    def updateData(self):
        self.updateSubForms()
        super(SubForm, self).updateData()

    def updateSubForms(self):
        self.subforms = []
        for iid, item in self.parentForm.getItems():
            subform =  component.getMultiAdapter(
                (self.context, self.request, self), ISubForm,
                name='crudeditsubform')
            subform.content = item
            subform.contentId = iid
            subform.update()
            subform.updateForm()
            self.subforms.append(subform)

    @button.buttonAndHandler(_('delete'), name='delete')
    def handleDelete(self, action):
        selected = self.selectedItems()
        if selected:
            self.status = _(u"Successfully deleted items.")
            for id, item in selected:
                try:
                    self.parentForm.remove((id, item))
                except ConflictError:
                    raise
                except:
                    # In case an exception is raised, we'll catch it
                    # and notify the user; in general, this is
                    # unexpected behavior:
                    self.status = _(u'Unable to remove one or more items.')
                    self.status_type = 'error'
                    break

            # We changed the amount of entries, so we update the
            # subforms again.
            self.updateSubForms()
        else:
            self.status = _(u"Please select items to delete.")
            self.status_type = 'error'

    @button.buttonAndHandler(
        _('save'), name='save',
        condition=lambda form: form.parentForm.update_fields)
    def handleSave(self, action):
        success = _(u"Successfully updated")
        partly_success = _(u"Some of your changes could not be applied.")
        status = no_changes = _(u"No changes made.")
        for subform in self.subforms:
            # With the ``extractData()`` call, validation will occur,
            # and errors will be stored on the widgets amongst other
            # places.  After this we have to be extra careful not to
            # call (as in ``__call__``) the subform again, since
            # that'll remove the errors again.  With the results that
            # no changes are applied but also no validation error is
            # shown.
            data, errors = subform.extractData()
            if errors:
                if status is no_changes:
                    status = subform.formErrorsMessage
                elif status is success:
                    status = partly_success
                continue
            del data['select']
            changes = subform.applyChanges(data)
            if changes:
                if status is no_changes:
                    status = success
                elif status is subform.formErrorsMessage:
                    status = partly_success

                # If there were changes, we'll update the view widgets
                # again, so that they'll actually display the changes
                for widget in  subform.widgets.values():
                    if widget.mode == DISPLAY_MODE:
                        widget.update()
                        event.notify(widget.AfterWidgetUpdateEvent(widget))
        self.status = status


class CrudEditSubForm(SubForm, form.EditForm):
    """An crud edit sub-form.
    """

    grok.name('crudeditsubform')
    grok.view(CrudEditForm)

    template = grok.PageTemplateFile('templates/crud_editrow.pt')

    # These are set by the parent form
    content = None
    contentId = None

    @property
    def fields(self):
        fields = field.Fields(self._selectField())
        crud_form = self.parentForm.parentForm
        update_fields = crud_form.update_fields
        if update_fields is not None:
            fields += field.Fields(update_fields)

        view_fields = crud_form.view_fields
        if view_fields is not None:
            view_fields = field.Fields(view_fields)
            for f in view_fields.values():
                f.mode = DISPLAY_MODE
                # This is to allow a field to appear in both view
                # and edit mode at the same time:
                if not f.__name__.startswith('view_'):
                    f.__name__ = 'view_' + f.__name__
            fields += view_fields

        return fields

    @property
    def prefix(self):
        return str('crudeditsubform.%s' % self.contentId)

    def link(self, name):
        return self.parentForm.parentForm.link(name , self.getContent())

    def getContent(self):
        return self.content

    def _selectField(self):
        select_field = field.Field(
            schema.Bool(__name__='select',
                        required=False,
                        title=_(u'select')))
        select_field.widgetFactory[INPUT_MODE] = singlecheckboxwidget_factory
        return select_field

    # XXX: The three following methods, 'getCombinedWidgets',
    # 'getTitleWidgets', and 'getNiceTitles' are hacks to support the
    # page template.  Let's get rid of them.
    def getCombinedWidgets(self):
        """Returns pairs of widgets to improve layout"""
        widgets = self.widgets.items()
        combined = []
        seen = set()
        for name, widget in list(widgets):
            if widget.mode == INPUT_MODE:
                view_widget = self.widgets.get('view_%s' % name)
                if view_widget is not None:
                    combined.append((widget, view_widget))
                    seen.add(view_widget)
                else:
                    combined.append((widget,))
            else:
                if widget not in seen:
                    combined.append((widget,))
        return combined

    def getTitleWidgets(self):
        return [widget[0] for widget in self.getCombinedWidgets()]

    def getNiceTitles(self):
        return [widget.field.title for widget in self.getTitleWidgets()]



# Macros to render z3c forms

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Z3CFormMacros(BrowserView):
    template = ViewPageTemplateFile('templates/z3cform.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

# Customization of widgets

@grok.subscribe(z3c.form.interfaces.IAfterWidgetUpdateEvent)
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

    grok.implements(ICancelButton)


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


# We customize that to prevent z3c.form to destroy the FileUpload Object.
class FileUploadDataConverter(
    converter.FileUploadDataConverter, grok.MultiAdapter):
    grok.adapts(silvaschema.IBytes,
                z3c.form.interfaces.IFileWidget)

    def toFieldValue(self, value):
        return value

    def toWidgetValue(self, value):
        return super(FileUploadDataConverter, self).toFieldValue(value)


# ContenteReferenceWidget
class IContentReferenceWidget(z3c.form.interfaces.IFieldWidget):
    pass


class ContentReferenceWidget(widget.Widget):
    grok.implements(IContentReferenceWidget)

    js = "reference.getReference( function(path, id, title) { document.getElementsByName('%s')[0].value = path;; }, '%s', '', true)"

    def onclick(self):
        content_url = absoluteURL(
            self.form.context.get_container(), self.request)
        return self.js % (self.name, content_url)

    def current_url(self):
        try:
            return self.field.get(self.form.getContent()).absolute_url()
        except AttributeError:
            return None


@grok.adapter(silvaschema.IContentReference, z3c.form.interfaces.IFormLayer)
@grok.provider(z3c.form.interfaces.IFieldWidget)
def ContentReferenceFieldWidget(field, request):
    return widget.FieldWidget(field, ContentReferenceWidget(request))


class ContentReferenceDataConverter(
    z3c.form.converter.BaseDataConverter, grok.MultiAdapter):
    grok.adapts(silvaschema.IContentReference, IContentReferenceWidget)

    def toFieldValue(self, value):
        container = self.widget.form.context.get_container()
        return self.field.fromRelativePath(container, value)

    def toWidgetValue(self, value):
        container = self.widget.form.context.get_container()
        return self.field.toRelativePath(container, value)
