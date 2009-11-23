# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

    >>> browser = Browser()
    >>> logAsUser(app, 'manager')

 We grok this test file:

    >>> grok('silva.core.views.tests.grok.views')

 Now we add a folder:

    >>> factory = app.root.manage_addProduct['Silva']
    >>> id = factory.manage_addFolder('myfolder', 'My Folder')
    >>> app.root.myfolder
    <Silva Folder instance myfolder>
    >>> browser.open('http://localhost/root/myfolder/mytestview')
    >>> browser.url
    'http://localhost/root/myfolder/mytestview'
    >>> browser.headers['status']
    '200 Ok'
    >>> print browser.contents
    <div>
      <h1>A Folder</h1>
    </div>

We can do HEAD requests:

    >>> reply = http('HEAD /root/myfolder/mytestview HTTP/1.1')
    >>> reply.header_output.headers
    {'Content-Length': '0',
     'Content-Type': 'text/html;charset=utf-8',
     'Cache-Control': 'max-age=86400, must-revalidate'}
    >>> reply.getBody()
    ''

If the view is private you should not have cache headers

    >>> from Products.Silva.tests import SilvaTestCase
    >>> import base64
    >>> AUTH_TOKEN = '%s:%s' % ('manager', SilvaTestCase.user_password)
    >>> AUTH = 'Authorization: Basic %s' % base64.b64encode(AUTH_TOKEN)
    >>> from Products.Silva.adapters.interfaces import IViewerSecurity
    >>> IViewerSecurity(app.root.myfolder).setMinimumRole('Authenticated')
    >>> reply = http('GET /root/myfolder/myprivateview HTTP/1.1\\r\\n%s' % AUTH)
    >>> reply.header_output.status
    200
    >>> reply.getBody()
    ''
    >>> reply.header_output.headers
    {'Content-Length': '0',
     'Content-Type': 'text/html;charset=utf-8',
     'Cache-Control': 'max-age=86400, must-revalidate'}
"""


from Products.Silva.Folder import Folder
from silva.core.views import views as silvaviews
from five import grok


class MyFolderView(silvaviews.View):
    grok.name('mytestview')
    grok.context(Folder)


class MyPrivateFolderView(silvaviews.View):
    grok.name('myprivateview')
    grok.context(Folder)
    grok.require('zope2.ViewManagementScreens')

    def render(self):
        return "Hello render!"


