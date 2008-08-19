# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
from zope.i18n import translate

from five import grok
import urllib

from Products.SilvaLayout.interfaces import IPreviewLayer

from silva.core.views.interfaces import IFeedbackView, IZMIView, ISilvaView
from silva.core import conf as silvaconf

# Simple views

class SilvaGrokView(grok.View):
    """Grok View on Silva objects.
    """

    silvaconf.baseclass()

    def publishTraverse(self, request, name):
        """In Zope2, if you give a name, index_html is appended to it.
        """
        if name == 'index_html':
            return self
        return super(View, self).publishTraverse(request, name)

    def redirect(self, url):
        # Override redirect to send status information if there is.
        if IFeedbackView.providedBy(self):
            message = self.status
            if message:
                message = translate(message)
                if isinstance(message, unicode):
                    # XXX This won't be decoded correctly at the other end.
                    message = message.encode('utf8')
                to_append = urllib.urlencode({'message': message,
                                              'message_type': self.status_type,})
                join_char = '?' in url and '&' or '?'
                super(SilvaGrokView, self).redirect(url + join_char + to_append)
                return
        super(SilvaGrokView, self).redirect(url)


class ZMIView(SilvaGrokView):
    """View in ZMI.
    """

    grok.implements(IZMIView)

    silvaconf.baseclass()

class View(SilvaGrokView):
    """View on Silva object, support view and preview
    """

    grok.implements(ISilvaView)

    silvaconf.baseclass()
    silvaconf.name(u'content.html')

    @zope.cachedescriptors.property.CachedProperty
    def is_preview(self):
        return IPreviewLayer.providedBy(self.request)

    @zope.cachedescriptors.property.CachedProperty
    def content(self):
        if self.is_preview:
            return self.context.get_previewable()
        return self.context.get_viewable()

    def namespace(self):
        return {'content': self.content}

