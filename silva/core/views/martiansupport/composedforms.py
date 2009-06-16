# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import grokcore.viewlet
from grokcore.view.meta.views import default_view_name
import grokcore.component
import martian

import zope.component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core.views.interfaces import ISubForm
from silva.core.views.z3cforms import SubForm


class SubFormGrokker(martian.ClassGrokker):

    martian.component(SubForm)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.view)
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return super(SubFormGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, view, name, **kw):
        if not factory.prefix:
            factory.prefix = name
        adapts = (context, layer, view)
        config.action(
            discriminator=('adapter', adapts, ISubForm, name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, ISubForm, name),
            )
        return True

