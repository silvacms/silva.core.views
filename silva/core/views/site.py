# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five import BrowserView

class VirtualSite(BrowserView):

    def get_root(self):
        root = self.get_virtual_root()
        if root is None:
            return self.context.get_root()
        return root

    def get_virtual_root(self):
        root_path = self.get_virtual_path()
        if root_path is None:
            return None

        return self.context.aq_inner.restrictedTraverse(root_path, None)

    def get_virtual_path(self):
        try:
            root_path = self.request['VirtualRootPhysicalPath']
        except (AttributeError, KeyError), err:
            root_path =  None

        return root_path

