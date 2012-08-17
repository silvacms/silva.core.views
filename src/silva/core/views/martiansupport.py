# -*- coding: utf-8 -*- 
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt 


from five import grok
from grokcore.view.meta.views import TemplateGrokker
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import grokcore.component
import martian

from .interfaces import IRender
from .views import Render


class RenderLayoutGrokker(TemplateGrokker):
    martian.component(Render)

    def has_render(self, factory):
        render = getattr(factory, 'render', None)
        base_method = getattr(render, 'base_method', False)
        return render is not None and not base_method

    def has_no_render(self, factory):
        render = getattr(factory, 'render', None)
        base_method = getattr(render, 'base_method', False)
        return render is None or base_method


class RenderGrokker(martian.ClassGrokker):
    martian.component(Render)
    martian.directive(grok.context)
    martian.directive(grok.layer, default=IDefaultBrowserLayer)
    martian.directive(grok.provides, default=IRender)
    martian.directive(grok.name)

    def execute(self, factory, config, context, layer, provides, name, **kw):
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, provides, name),
            callable=grokcore.component.provideAdapter,
            args=(factory, adapts, provides, name),
            )
        return True
