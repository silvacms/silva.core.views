# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.formlib import form
from zope import event
from zope import interface
from zope import lifecycleevent

from Products.Five.formlib import formbase
from Products.Silva.i18n import translate as _
from Products.Silva.interfaces import IVersionedContent
from Products.Silva.ViewCode import ViewCode

from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, SilvaMixinEditForm
from silva.core.views.views import SMIView
from silva.core.views.interfaces import IDefaultAddFields, ISilvaFormlibForm

# Forms


class SilvaGrokForm(SilvaMixinForm, ViewCode):
    """Silva Grok form for formlib.
    """

    interface.implements(ISilvaFormlibForm)

    @property
    def status_type(self):
        return (self.errors and 'error' or 'feedback') or self._status_type


class PageForm(SilvaGrokForm, formbase.PageForm, SMIView):
    """Generic form.
    """



class AddForm(SilvaMixinAddForm, SilvaGrokForm, formbase.AddForm, SMIView):
    """Add form.
    """


    def setUpWidgets(self, ignore_request=False):
        # Add missing fields from IDefaultAddFields
        field_to_add = form.FormFields()
        for field in IDefaultAddFields:
            if self.form_fields.get(field) is None:
                field_to_add += form.FormFields(IDefaultAddFields[field])
        if field_to_add:
            self.form_fields = field_to_add + self.form_fields
        # Setup widgets
        super(AddForm, self).setUpWidgets(ignore_request)

    @form.action(_(u"save"), condition=form.haveInputWidgets)
    def handle_save(self, **data):
        obj = self.createAndAdd(data)
        self.redirect('%s/edit' % self.context.absolute_url())

    @form.action(_(u"save + edit"), condition=form.haveInputWidgets)
    def handle_save_and_enter(self, **data):
        obj = self.createAndAdd(data)
        self.redirect('%s/edit' % obj.absolute_url())



class EditForm(SilvaMixinEditForm, SilvaGrokForm, formbase.EditForm, SMIView):
    """Edition form.
    """


    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        # We should use the editable version to setup the widgets.
        editable_obj =  self.context.get_editable()
        self.versioned_content = IVersionedContent.providedBy(self.context)
        if editable_obj is None:
            # If there is no editable version, create an empty list of fields.
            self.widgets = form.Widgets([], self.prefix)
            self.propose_new_version = self.versioned_content
            self.is_editable = False
        else:
            self.widgets = form.setUpEditWidgets(
                self.form_fields, self.prefix, editable_obj, self.request,
                adapters=self.adapters, ignore_request=ignore_request)

    @form.action(_("save"), condition=form.haveInputWidgets)
    def handle_edit_action(self, **data):
        editable_obj = self.context.get_editable()
        if form.applyChanges(editable_obj, self.form_fields, data, self.adapters):
            event.notify(lifecycleevent.ObjectModifiedEvent(editable_obj))
            self.status = _(u'${meta_type} changed.',
                            mapping={'meta_type': self.context.meta_type,})
        else:
            self.status = _(u'No changes')


# Macros to render formlib forms

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class FormlibMacros(BrowserView):
    template = ViewPageTemplateFile('templates/formlib.pt')

    def __getitem__(self, key):
        return self.template.macros[key]
