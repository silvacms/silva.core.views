# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import queryMultiAdapter
from zope.component import getSiteManager
from zope.component.interfaces import IFactory
from zope import interface
import zope.cachedescriptors.property

from Products.Silva.interfaces import IVersionedContent
from AccessControl import getSecurityManager

import grokcore.view
import martian

from silva.core.views.interfaces import IFeedbackView
from silva.core.conf.utils import getSilvaViewFor
from silva.core import conf as silvaconf

class SilvaMixinForm(object):
    """Silva grok form mixin.
    """

    interface.implements(IFeedbackView)

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
        # Return message_type for status.
        return (self.errors and 'error' or 'feedback') or self._status_type



class SilvaMixinAddForm(object):
    """Silva add form mixin.
    """

    def _silvaView(self):
        view_registry = self.context.service_view_registry
        ## Then you add a element, you have the edit view of the
        ## container wrapped by the add view.
        parent_view = super(SilvaMixinAddForm, self)._silvaView()
        return view_registry.get_view('add', 'Five Content').__of__(parent_view)


class SilvaMixinEditForm(object):
    """Silva edit form mixin.
    """

    ## If we refactor the Silva views correctly, we should be able to
    ## remove the two followings property, and use the same template
    ## than a PageForm. if.

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


# Grokkers for forms.

class AddFormGrokker(martian.ClassGrokker):
    """Grok add form and register them as factories.
    """

    martian.component(SilvaMixinAddForm)
    martian.directive(silvaconf.name)

    def execute(self, form, name, **kw):
        sm = getSiteManager()
        sm.registerUtility(form, IFactory, name=name)
        return True
