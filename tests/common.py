# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from testfixtures import Replacer

class SourceMixin(object):
    
    def setUp(self):
        def get_source():
            return 'default_source'
        self.r = Replacer()
        self.r.replace('configurator._api.get_source', get_source)

    def tearDown(self):
        self.r.restore()
        
