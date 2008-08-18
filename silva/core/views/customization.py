# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.app.apidoc.presentation import getViews
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope import component

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.Silva.BaseService import SilvaService
from Products.Silva.helpers import add_and_edit
from Products.Silva import interfaces as silva_interfaces

from five.customerize.browser import mangleAbsoluteFilename
from silva.core.views.ttwtemplates import TTWViewTemplate

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import ISilvaView


class CustomizationService(Folder, SilvaService):

    meta_type = 'Silva Customization Service'

    silvaconf.icon('customization.png')
    silvaconf.factory('manage_addCustomizationServiceForm')
    silvaconf.factory('manage_addCustomizationService')

    manage_options = (
        {'label':'Customize', 'action':'manage_customization'},
        ) + Folder.manage_options


class ManageCustomTemplates(silvaviews.ZMIView):

    silvaconf.context(CustomizationService)
    silvaconf.name('manage_customization')
    silvaconf.require('zope2.ViewManagementScreens')

    def update(self):
        self.availableTemplates = []
        self.selectedInterface = self.request.form.get('interface', None)
        if self.selectedInterface:

            templates = []

            interface = component.getUtility(IInterface, name=self.selectedInterface)
            for reg in getViews(interface, IBrowserRequest):
                if ((hasattr(reg.factory, '__name__') and reg.factory.__name__.startswith('SimpleViewClass')) or
                    ISilvaView.implementedBy(reg.factory)):
                    templates.append(reg)

            for reg in sorted(templates, key=lambda r: r.name):
                if not reg.required[0].isOrExtends(silva_interfaces.ISilvaObject):
                    continue
                customizable = True
                if ISilvaView.implementedBy(reg.factory):
                    if hasattr(reg.factory, 'template'):
                        template = reg.factory.template._template.filename
                    else:
                        template = u'direct rendering'
                        customizable = False
                    config = u'Grok page template'
                else:
                    template = reg.factory.index.filename
                    config = mangleAbsoluteFilename(reg.info.file)
                self.availableTemplates.append({
                        'name': reg.name,
                        'for': reg.required[0].__identifier__,
                        'layer': reg.required[1].__identifier__,
                        'template': template,
                        'config': config,
                        'customizable': customizable
                        })


    def availablesInterfaces(self):
        interfaces = component.getUtilitiesFor(IInterface)
        return [name for name, interface in interfaces if interface.isOrExtends(silva_interfaces.ISilvaObject)]
        

class ManageViewTemplate(silvaviews.ZMIView):

    silvaconf.context(CustomizationService)
    silvaconf.name('manage_template')
    silvaconf.require('zope2.ViewManagementScreens')

    def update(self):
        assert 'for' in self.request.form
        assert 'name' in self.request.form

        self.name = self.request.form['name']
        self.for_name = self.request.form['for']
        self.layer_name = self.request.form['layer']
        self.interface = component.getUtility(IInterface, name=self.for_name)

        view = None
        for reg in getViews(self.interface, IBrowserRequest):
            if (reg.name == self.name and 
                reg.required[0].__identifier__ == self.for_name and
                reg.required[1].__identifier__ == self.layer_name):
                view = reg
                break
        if view is None:
            raise ValueError, 'Template not found'

        self.reg = reg
        self.factory = reg.factory
        if ISilvaView.implementedBy(reg.factory):
            self.code = open(self.factory.template._template.filename, 'rb').read()
        else:
            self.code = open(self.factory.index.filename, 'rb').read()

class ManageCreateCustomTemplate(ManageViewTemplate):

    silvaconf.name('manage_createCustom')


    def permission(self):
        permissions = self.factory.__ac_permissions__
        for permission, methods in permissions:
            if methods[0] in ('', '__call__',):
                return permission

    def update(self):
        super(ManageCreateCustomTemplate, self).update()

        template_id = '%s-%s-%s' % (self.for_name.split('.')[-1],
                                    self.layer_name.split('.')[-1],
                                    self.name)

        viewclass = self.factory.__bases__[0]
        permission = self.permission()

        new_template = TTWViewTemplate(template_id, self.code, 
                                       view=viewclass, permission=permission)
        
        self.context._setObject(template_id, new_template)

        manager = self.context.get_root().getSiteManager()
        manager.registerAdapter(new_template, required=self.reg.required, 
                                provided=self.reg.provided, name=self.name)

        new_template = getattr(self.context, template_id)
        self.redirect(new_template.absolute_url() + '/manage_workspace')

                                       
    def render(self):
        return u'Customized.'


manage_addCustomizationServiceForm = PageTemplateFile(
    "www/customizationServiceAdd", globals(),
    __name__='manage_addCustomizationServiceForm')

def manage_addCustomizationService(self, id, REQUEST=None):
    """Add a Customization Service."""
    object = CustomizationService(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''
