# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from . import api
from .section import Section

# build the schema for schemas
Schema = Section()


key = Section()
key.name="*"
key.count="*"
key.type="key"
Schema.key = key

section = Section()
section.name="*"
section.count="*"
section.type="section"
Schema.section = section

'''
<section type="element" count="+"/>

<section named="key" implements="element">
</section>
<section named="key" implements="element">
</section>
'''
