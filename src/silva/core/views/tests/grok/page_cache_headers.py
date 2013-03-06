# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
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

    >>> browser = getBrowser()
    >>> browser.open('http://localhost/root/myfolder/mytestpage')
    200
    >>> browser.headers
    {'content-length': '43',
     'content-type': 'text/html;charset=utf-8',
     'cache-control': 'max-age=86400, must-revalidate'}
    >>> browser.contents
    u'Layout: this is a content page!, end of it.'

 We can do HEAD requests:

    >>> browser.open('/root/myfolder/mytestpage', method='HEAD')
    204
    >>> browser.headers
    {'content-length': '0',
     'content-type': 'text/html;charset=utf-8',
     'cache-control': 'max-age=86400, must-revalidate'}
    >>> browser.contents
    u''

 We now create a protected folder:

    >>> from silva.core.interfaces.auth import IAccessSecurity
    >>> IAccessSecurity(root.myfolder).minimum_role = 'Authenticated'

 If the view is private you should not have cache headers:

    >>> browser.login('manager')
    >>> browser.open('http://localhost/root/myfolder/mytestpage')
    200
    >>> browser.headers
    {'content-length': '43',
     'expires': 'Mon, 26 Jul 1997 05:00:00 GMT',
     'content-type': 'text/html;charset=utf-8',
     'pragma': 'no-cache',
     'cache-control': 'no-cache, must-revalidate, post-check=0, pre-check=0'}
    >>> browser.contents
    u'Layout: this is a content page!, end of it.'

"""

from Products.Silva.Folder import Folder
from silva.core.views import views as silvaviews
from grokcore.layout import ILayout, layout
from five import grok


class IMySimpleLayout(ILayout):
    pass


class MySimpleLayout(silvaviews.Layout):
    grok.provides(IMySimpleLayout)

    def render(self):
        return "".join(("Layout: ", self.view.content(), ", end of it."))


class MyFolderPage(silvaviews.Page):
    grok.name('mytestpage')
    grok.context(Folder)
    layout(IMySimpleLayout)

    def render(self):
        return "this is a content page!"
