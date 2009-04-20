# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import martian

from zope.component import provideUtility
from zope.component.interfaces import IFactory

from silva.core.views.baseforms import SilvaMixinAddForm
from silva.core import conf as silvaconf


class AddFormGrokker(martian.ClassGrokker):
    """Grok add form and register them as factories.
    """

    martian.component(SilvaMixinAddForm)
    martian.directive(silvaconf.name)

    def execute(self, form, name, config, **kw):
        config.action(
            discriminator = ('utility', IFactory, name),
            callable = provideUtility,
            args = (form, IFactory, name),
            )
        return True

