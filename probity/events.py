import os

class BaseEvent(object):
    pass

class FileEvent(BaseEvent):
    folder = None

    def __init__(self, base_path, path, checksum, size=None):
        self.path = path
        self.checksum = checksum
        self.name = path.split('/')[-1]
        self.fs_path = os.path.join(base_path, path)
        self.size = size

    def __str__(self):
        return '%s: %s\n' % (self.name, self.checksum)

class FolderBeginEvent(BaseEvent):
    folder = 'begin'
    checksum = None

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]

    def __str__(self):
        return '[begin folder "%s"]\n' % self.name

class FolderEndEvent(BaseEvent):
    folder = 'end'

    def __init__(self, path, checksum):
        self.path = path
        self.checksum = checksum
        self.name = path.split('/')[-1]

    def __str__(self):
        return '[end folder "%s": %s]\n' % (self.name, self.checksum)
