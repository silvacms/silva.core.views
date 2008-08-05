# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.configuration.name import resolve
from zope.component import queryAdapter
from zope.formlib import form
from zope import event
from zope import interface
from zope import lifecycleevent

from Products.Five.formlib import formbase
from Products.Silva.i18n import translate as _
from Products.Silva.interfaces import IVersionedContent
from Products.Silva.ViewCode import ViewCode
from Products.Silva.ExtensionRegistry import extensionRegistry

from grokcore.formlib import action
from grokcore.formlib.components import GrokForm
import grokcore.view

from silva.core.views.baseforms import SilvaMixinForm, SilvaMixinAddForm, SilvaMixinEditForm
from silva.core.views.views import SilvaGrokView
from silva.core.views.interfaces import IDefaultAddFields, ISilvaFormlibForm
from silva.core.conf.utils import getFactoryName
from silva.core import conf as silvaconf

# Forms


class SilvaGrokForm(SilvaMixinForm, GrokForm, ViewCode):
    """Silva Grok form for formlib.
    """

    interface.implements(ISilvaFormlibForm)
    silvaconf.baseclass()

    def __init__(self, context, request):
        super(SilvaGrokForm, self).__init__(context, request)
        # Missing init code of grokcore.view.components.Views
        self.__name__ = self.__view_name__
        self.static = queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)


class PageForm(SilvaGrokForm, formbase.PageForm, SilvaGrokView):
    """Generic form.
    """

    silvaconf.baseclass()


class AddForm(SilvaMixinAddForm, SilvaGrokForm, formbase.AddForm, SilvaGrokView):
    """Add form.
    """

    silvaconf.baseclass()

    template = grokcore.view.PageTemplateFile('templates/add_form.pt')


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

    @action(_(u"save"), condition=form.haveInputWidgets)
    def handle_save(self, **data):
        obj = self.createAndAdd(data)
        self.redirect('%s/edit' % self.context.absolute_url())

    @action(_(u"save + edit"), condition=form.haveInputWidgets)
    def handle_save_and_enter(self, **data):
        obj = self.createAndAdd(data)
        self.redirect('%s/edit' % obj.absolute_url())

    def createAndAdd(self, data):
        addable = filter(lambda a: a['name'] == self.__name__,
                         extensionRegistry.get_addables())
        if len(addable) != 1:
            raise ValueError, "Content cannot be found. " \
               "Check that the name of add is the meta type of your content." 
        addable = addable[0]
        factory = getattr(resolve(addable['instance'].__module__),
                          getFactoryName(addable['instance']))
        # Build the content
        obj_id = str(data['id'])
        factory(self.context, obj_id, data['title'])
        obj = getattr(self.context, obj_id)

        editable_obj = obj.get_editable()
        for key, value in data.iteritems():
            if key not in IDefaultAddFields:
                setattr(editable_obj, key, value)

        # Update last author information
        obj.sec_update_last_author_info()
        self.context.sec_update_last_author_info()

        # Set status
        self.status = _(u'Created ${meta_type} "${obj_id}".',
                        mapping={'obj_id': obj_id,
                                 'meta_type': obj.meta_type,})

        return obj



class EditForm(SilvaMixinEditForm, SilvaGrokForm, formbase.EditForm, SilvaGrokView):
    """Edition form.
    """

    silvaconf.baseclass()
    silvaconf.name(u'tab_edit')


    template = grokcore.view.PageTemplateFile('templates/edit_form.pt')

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
        
    @action(_("save"), condition=form.haveInputWidgets)
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
