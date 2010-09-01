# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
 We grok this test file:
    >>> grok('silva.core.views.tests.grok.page_cache_headers')

 Now we add a folder:

    >>> root = getRootFolder()
    >>> factory = root.manage_addProduct['Silva']
    >>> _ = factory.manage_addFolder('myfolder', 'My Folder')
    >>> root.myfolder
    <Folder at /root/myfolder>

 When requesting the view the response should include cache control
 headers:

    >>> browser = Browser()
    >>> browser.open('http://localhost/root/myfolder/mytestpage')
    >>> browser.status
    '200 OK'
    >>> browser.contents
    'Layout: this is a content page!, end of it.'
    >>> browser.headers.has_key('cache-control')
    True
    >>> browser.headers['Cache-Control']
    'max-age=86400, must-revalidate'

 We can do HEAD requests:

    >>> reply = http('HEAD /root/myfolder/mytestpage HTTP/1.1', parsed=True)
    >>> reply.getHeaders()
    {'Content-Length': '0',
     'Content-Type': 'text/html;charset=utf-8',
     'Cache-Control': 'max-age=86400, must-revalidate'}
    >>> reply.getBody()
    ''

 We now create a protected folder:

    >>> from silva.core.interfaces.auth import IAccessSecurity
    >>> IAccessSecurity(root.myfolder).minimum_role = 'Authenticated'

 If the view is private you should not have cache headers:

    >>> browser.addHeader("Authorization", 'Basic manager:manager')
    >>> browser.open('http://localhost/root/myfolder/mytestpage')
    >>> browser.status
    '200 OK'
    >>> browser.contents
    'Layout: this is a content page!, end of it.'
    >>> browser.headers.has_key('cache-control')
    True
    >>> browser.headers['Cache-Control']
    'no-cache, must-revalidate, post-check=0, pre-check=0'
    >>> browser.headers.has_key('pragma')
    True
    >>> browser.headers['Pragma']
    'no-cache'

"""

from Products.Silva.Folder import Folder
from silva.core.views import views as silvaviews
from infrae.layout import ILayout, layout
from five import grok


class IMySimpleLayout(ILayout):
    pass


class MySimpleLayout(silvaviews.Layout):
    layout(IMySimpleLayout)

    def render(self):
        return "".join(("Layout: ", self.view.content(), ", end of it."))


class MyFolderPage(silvaviews.Page):
    grok.name('mytestpage')
    grok.context(Folder)
    layout(IMySimpleLayout)

    def render(self):
        return "this is a content page!"
