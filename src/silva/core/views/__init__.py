# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf

silvaconf.extensionName('silva.core.views')
silvaconf.extensionTitle('Silva Core Views')
silvaconf.extensionSystem()

import zope.deferredimport
zope.deferredimport.deprecated(
    'Forms moved into silva.core.forms.',
    forms = 'silva.core.forms.forms',
    z3cforms = 'silva.core.forms.z3cforms')
