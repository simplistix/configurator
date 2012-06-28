from configurator._api import API

def parse(source,text):
    node = API()
    for i,line in enumerate(text.split('\n')):
        line_no = i+1
        line = line.strip()
        if not line:
            continue
        key,value = line.split(' ',1)
        node.set(key,value.strip(),'line %i of %s' % (line_no,source))
    return node
