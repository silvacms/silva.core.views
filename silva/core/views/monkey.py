# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Five, the best breed of the world.

import Products.Five.browser.resource

def call(self, request):
    resource = self.resource(self._ResourceFactory__rsrc, request)
    # Be sure that __name__ is set correctly.
    resource.__name__ = self._ResourceFactory__name
    return resource

Products.Five.browser.resource.ResourceFactory.__call__ = call
