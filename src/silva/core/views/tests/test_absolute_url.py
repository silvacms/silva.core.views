from Products.Silva.testing import FunctionalLayer, http

from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

import unittest
from urllib import quote

class AbsTestRequest(TestRequest):
    """new TestRequest class which adds some missing functionality from
       ZPublisher.HTTPRequest, namely physicalPathToURL"""
    
    def __init__(self, **kw):
        #set a default script
        self._script = []
        super(AbsTestRequest, self).__init__(**kw)
    
    def physicalPathToVirtualPath(self, path):
        """ Remove the path to the VirtualRoot from a physical path """
        #XXX the tests don't check virtual sites, so skipping this
        return path

    def physicalPathToURL(self, path, relative=0):
        """ Convert a physical path into a URL in the current context """
        path = self._script + map(quote, self.physicalPathToVirtualPath(path))
        if relative:
            path.insert(0, '')
        else:
            #don't want a double '//' between server url and paath
            if path[0] == '':
                path[0] = self['SERVER_URL']
            else:
                path.insert(0, self['SERVER_URL'])
        return '/'.join(path)

class AbsoluteUrlTestCase(unittest.TestCase):
    layer = FunctionalLayer
    
    def setUp(self):
        self.root = self.layer.get_application()
        
        self.root.manage_addProduct['Silva'].manage_addFolder('folder',
                                                              'folder')
        self.root.folder.manage_addProduct['Silva'].manage_addAutoTOC('index',
                                                                      'index')
        
    def test_index_absurl(self):
        #test generating absolute url to index doc, should be no '/' but not
        # '/index' (for canonicalization purposes)

        self.request = AbsTestRequest()
        ad = getMultiAdapter((self.root.folder, self.request),
                             name='absolute_url')
        self.assertEquals(ad(), 'http://127.0.0.1/root/folder/')
        
        ad = getMultiAdapter((self.root.folder.index, self.request),
                             name='absolute_url')
        self.assertEquals(ad(), 'http://127.0.0.1/root/folder/')
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AbsoluteUrlTestCase))
    return suite