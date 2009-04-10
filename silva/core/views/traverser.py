# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from ZPublisher.BaseRequest import DefaultPublishTraverse

class SilvaPublishTraverse(DefaultPublishTraverse):

    def browserDefault(self, request):
        # We don't want to lookup five views if we have other than a
        # GET or POST request.
        if request.method in ['GET', 'POST',]:
            return super(SilvaPublishTraverse, self).browserDefault(request)
        return self.context, ()
