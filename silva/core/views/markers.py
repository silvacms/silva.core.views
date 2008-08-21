# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.interface import PersistentInterfaceClass
from zope.interface.interfaces import IInterface
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from Products.Silva.BaseService import ZMIObject
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import ISilvaObject

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews

from interfaces import ISilvaCustomizableType, ISilvaCustomizable
from customization import CustomizationManagementView

class CustomizationMarker(PersistentInterfaceClass, ZMIObject):

    meta_type = 'Silva Customization Marker'

    silvaconf.icon('customization.png')
    silvaconf.factory('manage_addCustomizationMarkerForm')
    silvaconf.factory('manage_addCustomizationMarker')

    def __init__(self, name, doc=None):
        PersistentInterfaceClass.__init__(self, name=name, bases=(ISilvaCustomizable,), __doc__=doc)
        ZMIObject.__init__(self, name)

    @property
    def markerId(self):
        return 'silva.core.views.markers.%s' % self.__name__


manage_addCustomizationMarkerForm = PageTemplateFile(
    "www/customizationMarkerAdd", globals(),
    __name__='manage_addCustomizationMarkerForm')

def manage_addCustomizationMarker(self, name, REQUEST=None):
    """Add a Customization Marker.
    """

    marker = CustomizationMarker(name)
    self._setObject(name, marker)
    add_and_edit(self, name, REQUEST)
    return ''


@silvaconf.subscribe(CustomizationMarker, IObjectAddedEvent)
def registerInterface(marker, event):
    sm = marker.getSiteManager()
    for iface_type in [IInterface, ISilvaCustomizableType,]:
        sm.registerUtility(marker, iface_type, marker.markerId)


@silvaconf.subscribe(CustomizationMarker, IObjectRemovedEvent)
def unregisterInterface(marker, event):
    sm = marker.getSiteManager()
    for iface_type in [IInterface, ISilvaCustomizableType,]:
        sm.unregisterUtility(marker, iface_type, marker.markerId)


class ManageCustomizeMarker(CustomizationManagementView):

    silvaconf.name('manage_customization')
    silvaconf.context(ISilvaObject)

