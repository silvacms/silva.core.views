# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.container.interfaces import IObjectRemovedEvent
import zope.component

import Acquisition
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from Products.Five.metaclass import makeClass
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from silva.core.views.interfaces import IGrokCustomizable, ICustomizedTemplate


class TTWViewTemplate(ZopePageTemplate):
    """A template class used to generate Zope 3 views TTW"""

    meta_type="Silva TTW View Template"
    grok.implements(ICustomizedTemplate)

    manage_options = (
        ZopePageTemplate.manage_options[0],
        ) + ZopePageTemplate.manage_options[2:]

    def __init__(self, id, text=None, content_type='text/html', strict=True,
                 encoding='utf-8', view=None, permission=None, name=None):
        self.view = view
        self.permission = permission
        self.name = name
        super(TTWViewTemplate, self).__init__(
            id, text, content_type, encoding, strict)

    def __call__(self, *args):
        #XXX raise a sensible exception if context and request are
        # omitted, IOW, if someone tries to render the template not as
        # a view.
        sm = getSecurityManager()
        if self.permission:
            if not sm.checkPermission(self.permission, args[0]):
                raise Unauthorized('The current user does not have the '
                                   'required "%s" permission'
                                   % self.permission)

        class_ = makeClass(
            'FrankensteinTTWTemplate',
            (TTWViewTemplateRenderer, self.view),
            {'__name__': self.name,
             '__view_name__': self.name,
             'module_info': FakeModuleInfoForGrok(self.view.__module__)})

        return class_(self, self.view, args)

    # overwrite Shared.DC.Scripts.Binding.Binding's before traversal
    # hook that would prevent to look up views for instances of this
    # class.
    def __before_publishing_traverse__(self, self2, request):
        pass


class FakeModuleInfoForGrok(object):

    def __init__(self, path):
        self.package_dotted_name = path


class TTWViewTemplateRenderer(Acquisition.Implicit):
    """The view object for the TTW View Template.

    When a TTWViewTemplate-based view is looked up, an object of this
    class is instantiated.  It holds a reference to the
    TTWViewTemplate object which it will use in the render process
    (__call__).
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, template, view, args):
        self.template = template
        view.__init__(self, *args)

    def __call__(self, *args, **kwargs):
        """Render the TTWViewTemplate-based view.
        """
        return self.render(*args, **kwargs)

    def render(self, *args, **kwargs):
        """Render the view
        """
        # we need to override the template's context and request as
        # they generally point to the wrong objects (a template's
        # context usually is what it was acquired from, which isn't
        # what the context is for a view template).
        bound_names = {'context': self.context,
                       'request': self.request,
                       'view': self}

        if IGrokCustomizable.providedBy(self):
            bound_names.update(self.default_namespace())
            self.update()
            if self.request.response.getStatus() in (302, 303):
                return

        return self.template._exec(bound_names, args, kwargs)



@grok.subscribe(TTWViewTemplate, IObjectRemovedEvent)
def unregisterViewWhenZPTIsDeleted(template, event):
    components = zope.component.getSiteManager(template)
    for view in components.registeredAdapters():
        if view.factory == template:
            components.unregisterAdapter(
                view.factory, view.required, view.provided, view.name)
            break
