# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.configuration.name import resolve
from zope.component import queryMultiAdapter
from zope import interface
import zope.cachedescriptors.property

from Products.Silva.i18n import translate as _
from Products.Silva.interfaces import IVersionedContent
from Products.Silva.ExtensionRegistry import extensionRegistry
from AccessControl import getSecurityManager

import grokcore.view

from silva.core.views.interfaces import IFeedback, IDefaultAddFields
from silva.core.conf.utils import getSilvaViewFor, getFactoryName
from silva.core import conf as silvaconf

class SilvaMixinForm(object):
    """Silva grok form mixin.
    """

    interface.implements(IFeedback)

    silvaconf.baseclass()

    template = grokcore.view.PageTemplateFile('templates/form.pt')

    def __init__(self, context, request):
        super(SilvaMixinForm, self).__init__(context, request)

        # Set model on request like SilvaViews
        self.request['model'] = context
        # Set id on template some macros uses template/id
        self.template._template.id = self.__view_name__

        # Default feedback
        self._status_type = None
        

    def __call__(self, message=None, message_type=None):
        if message:
            self.status = message
            if message_type:
                self._status_type = message_type
            else:
                self._status_type = "feedback"
        return super(SilvaMixinForm, self).__call__()

    def _silvaView(self):
        # Lookup the correct Silva edit view so forms are able to use
        # silva macros.
        return getSilvaViewFor(self.context, 'edit', self.context)

    def namespace(self):
        # This add to the template namespace global variable used in
        # Zope 2 and Silva templates.  Here should be bind at the
        # correct place in the Silva view registry so you should be
        # able to use silva macro in your templates.
        view = self._silvaView()
        return {'here': view,
                'user': getSecurityManager().getUser(),
                'container': self.context.aq_inner,}

    @zope.cachedescriptors.property.CachedProperty
    def form_macros(self):
        return queryMultiAdapter((self, self.request,), name='form-macros')

    @property
    def status_type(self):
        return self._status_type


class SilvaMixinAddForm(object):
    """Silva add form mixin.
    """

    template = grokcore.view.PageTemplateFile('templates/add_form.pt')

    def _silvaView(self):
        view_registry = self.context.service_view_registry
        ## Then you add a element, you have the edit view of the
        ## container wrapped by the add view.
        parent_view = super(SilvaMixinAddForm, self)._silvaView()
        return view_registry.get_view('add', 'Five Content').__of__(parent_view)


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
        self.status = _(u'Added ${meta_type} "${obj_id}".',
                        mapping={'obj_id': obj_id,
                                 'meta_type': obj.meta_type,})
        return obj



class SilvaMixinEditForm(object):
    """Silva edit form mixin.
    """

    ## If we refactor the Silva views correctly, we should be able to
    ## remove the two followings property, and use the same template
    ## than a PageForm. if.


    template = grokcore.view.PageTemplateFile('templates/edit_form.pt')
    silvaconf.name(u'tab_edit')

    versioned_content = False
    propose_new_version = False
    is_editable = True
    
    @property
    def propose_to_publish(self):
        if not IVersionedContent.providedBy(self.context):
            return False
        sm = getSecurityManager()
        return (self.context.get_unapproved_version() and
                sm.checkPermission('Approve Silva content', self.context))



    ## End of useless duplication.


