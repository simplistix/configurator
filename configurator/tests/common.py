# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from testfixtures import Replacer

class SourceMixin(object):
    
    def setUp(self):
        def get_source(level=''):
            return 'default_source'+str(level)
        self.r = Replacer()
        self.r.replace('configurator._api.get_source', get_source)
        self.r.replace('configurator.section.get_source', get_source)

    def tearDown(self):
        self.r.restore()
        
