class Comparator(object):
    def __init__(self, reference):
        self.reverse_ref = dict((v, k) for k, v in reference.iteritems())
        self.extra = set()

    def update(self, evt):
        if evt.folder is not None:
            return

        try:
            del self.reverse_ref[evt.checksum]
        except KeyError:
            self.extra.add(evt.path)

    def report(self):
        return {
            'missing': set(self.reverse_ref.itervalues()),
            'extra': self.extra,
        }
