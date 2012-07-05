from configurator import api
from configurator.section import Section

def parse(text, source=None):
    section = Section()
    node = api(section)
    for i,line in enumerate(text.split('\n')):
        line_no = i+1
        line = line.strip()
        if not line:
            continue
        key,value = line.split(' ',1)
        node.set(key,value.strip(),'line %i of %s' % (line_no,source))
    return node
