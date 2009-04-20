# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: layout.py 34685 2009-04-17 14:15:42Z sylvain $

import grokcore.component
import martian

import zope.component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core.views.interfaces import ILayout
from silva.core.views.views import Layout


class LayoutGrokker(martian.ClassGrokker):

    martian.component(Layout)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return super(LayoutGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, **kw):
        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory)
                )

        adapts = (context, layer)
        config.action(
            discriminator=('adapter', adapts, ILayout),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, ILayout),
            )
        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)
