import collections


class DefaultDictKeyAsArg(collections.defaultdict):
    """
    A normal defaultdict calls the default_factory function with no arguments.
    This variant allows for passing `key` as argument to default_factory instead.
    """

    def __missing__(self, key):
        if self.default_factory is not None:
            self[key] = self.default_factory(key)
            return self[key]
        else:
            super().__missing__(key)


def log_skipped_stdout(line_idx, msg):
    print('Skipping line {line_idx}: {msg}'.format(**locals()))
