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

"""

from Products.Silva.Folder import Folder
from silva.core.views import views as silvaviews
from five import grok


class MyFolderView(silvaviews.View):
    grok.name('mytestview')
    grok.context(Folder)



