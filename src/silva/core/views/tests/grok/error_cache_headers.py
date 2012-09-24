# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt
"""

 We grok this test file:
    >>> grok('silva.core.views.tests.grok.error_cache_headers')

 Now we add a folder:

    >>> root = getRootFolder()
    >>> factory = root.manage_addProduct['Silva']
    >>> _ = factory.manage_addFolder('myfolder', 'My Folder')
    >>> root.myfolder
    <Folder at /root/myfolder>

 When requesting the view the response should include cache control
 headers:

    >>> browser = getBrowser()
    >>> browser.open('http://localhost/root/myfolder/notexitingview')
    404
    >>> browser.headers
    {'content-length': '24',
     'expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
     'content-type': 'text/html;charset=utf-8',
     'pragma': 'no-cache',
     'cache-control': 'no-cache, must-revalidate, post-check=0, pre-check=0'}
    >>> browser.contents
    u"This page doesn't exists"

 We can do HEAD requests:

    >>> browser.open('/root/myfolder/notexistingview', method='HEAD')
    404

 This doesn't work as expected:
    # browser.headers
    {'content-length': '0',
     'content-type': 'text/html;charset=utf-8',
     'expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
     'pragma': 'no-cache',
     'cache-control': 'no-cache, must-revalidate, post-check=0, pre-check=0'}
    >>> browser.contents
    u''

"""

from five import grok
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import ErrorHeaders
from zope.publisher.interfaces import INotFound
from zope.publisher.interfaces.browser import IBrowserRequest


class NotFoundError(silvaviews.View):
    grok.name('error.html')
    grok.context(INotFound)

    def render(self):
        return "This page doesn't exists"


class NotFoundHeaders(ErrorHeaders):
    grok.adapts(IBrowserRequest, INotFound)

    def other_headers(self, headers):
        super(ErrorHeaders, self).other_headers(headers)
        self.response.setStatus(404)
