class BaseEvent(object):
    _str = None
    def __str__(self):
        if self._str is None:
            self._str = self._format()
        return self._str

    def _format(self):
        raise NotImplementedError

class FileEvent(BaseEvent):
    folder = None
    def __init__(self, path, checksum):
        self.path = path
        self.checksum = checksum
        self.name = path.split('/')[-1]

    def _format(self):
        return '%s: %s\n' % (self.name, self.checksum)

class FolderBeginEvent(BaseEvent):
    folder = 'begin'
    checksum = None
    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]

    def _format(self):
        return '[begin folder "%s"]\n' % self.name

class FolderEndEvent(BaseEvent):
    folder = 'end'
    def __init__(self, path, checksum):
        self.path = path
        self.checksum = checksum
        self.name = path.split('/')[-1]

    def _format(self):
        return '[end folder "%s": %s]\n' % (self.name, self.checksum)
