# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
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

from five import grok

from silva.core.views.interfaces import IFeedback, IDefaultAddFields
#from silva.core.conf.utils import getFactoryName

class SilvaMixinForm(object):
    """Silva grok form mixin.
    """

    interface.implements(IFeedback)

    grok.baseclass()

    template = grok.PageTemplateFile('templates/form.pt')

    def __init__(self, context, request):
        super(SilvaMixinForm, self).__init__(context, request)

        # Set model on request like SilvaViews
        self.request['model'] = self._silvaContext
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

    @zope.cachedescriptors.property.CachedProperty
    def form_macros(self):
        return queryMultiAdapter((self, self.request,), name='form-macros')

    @property
    def status_type(self):
        return self._status_type


class SilvaMixinAddForm(object):
    """Silva add form mixin.
    """

    template = grok.PageTemplateFile('templates/add_form.pt')

    vein = u'add'

    def _silvaView(self):
        view_registry = self.context.service_view_registry
        ## Then you add a element, you have the edit view of the
        ## container wrapped by the add view.
        parent_view = super(SilvaMixinAddForm, self)._silvaView()
        return view_registry.get_view('add', 'Five Content').__of__(parent_view)

    def create(self, parent, data):
        """Purely create the object. This method can be overriden to
        support custom creation needs.
        """
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
        factory(parent, obj_id, data['title'])
        obj = getattr(parent, obj_id)
        
        #now move to position, if 'add_object_position' is in the request
        position = self.request.get('add_object_position', None)
        if position:
            try:
                position = int(position)
                if position >= 0:
                    parent.move_to([obj_id], position)
            except ValueError:
                pass

        editable_obj = obj.get_editable()
        for key, value in data.iteritems():
            if key not in IDefaultAddFields:
                setattr(editable_obj, key, value)
        return obj

    def createAndAdd(self, data):
        """Create and add the new object.
        """
        parent = self.context.aq_inner
        try:
            obj = self.create(parent, data)
        except ValueError, msg:
            self.status = msg
            self.status_type = 'error'
            return None

        if obj is not None:
            # Update last author information
            obj.sec_update_last_author_info()
            parent.sec_update_last_author_info()

            # Set status
            self.status = _(u'Added ${meta_type} "${obj_id}".',
                            mapping={'obj_id': obj.id,
                                     'meta_type': obj.meta_type,})
        return obj


class SilvaMixinEditForm(object):
    """Silva edit form mixin.
    """

    ## If we refactor the Silva views correctly, we should be able to
    ## remove the two followings property, and use the same template
    ## than a PageForm. if.


    template = grok.PageTemplateFile('templates/edit_form.pt')
    grok.name(u'tab_edit')

    vein = u'edit'

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


