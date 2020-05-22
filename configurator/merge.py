

def merge_dict(context, source, target):
    result = target.copy()
    for key, source_value in source.items():
        if key in result:
            target_value = result[key]
        else:
            target_value = type(source_value)()
        try:
            value = context.merge(source_value, target_value)
        except TypeError:
            # can't merge, so overwrite
            value = source_value
        result[key] = value
    return result


def merge_list(context, source, target):
    return target + source


class MergeableDict(dict):

    def __add__(self, other):
        result = self.copy()
        result.update(other)
        return result


default_mergers = MergeableDict({
    dict: merge_dict,
    list: merge_list,
})


class MergeContext(object):

    mergers = default_mergers

    def __init__(self, mergers=None):
        if mergers is not None:
            self.mergers = mergers

    def merge(self, source, target):
        source_type = type(source)
        target_type = type(target)
        merger = self.mergers.get(target_type)
        if source_type is not target_type or merger is None:
            raise TypeError('Cannot merge {} with {}'.format(
                source_type, target_type
            ))
        return merger(self, source, target)
