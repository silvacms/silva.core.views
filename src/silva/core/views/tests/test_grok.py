from Products.Silva.tests.test_grok import suiteFromPackage
import unittest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suiteFromPackage('grok', 'silva.core.views.tests'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
