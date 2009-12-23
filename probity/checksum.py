from hashlib import sha1
import os
from os import path

BLOCK_SIZE = 65536

def file_sha1(file_path):
    sha1_hash = sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break
            sha1_hash.update(data)
    return sha1_hash.hexdigest()

def walk_item(base_path, current_path):
    item_path = path.join(base_path, current_path)
    if path.isfile(item_path):
        return [FileEvent(current_path, file_sha1(item_path))]
    elif path.isdir(item_path):
        return walk_folder(base_path, current_path)
    else:
        raise NotImplementedError

def walk_folder(base_path, current_path):
    folder_path = path.join(base_path, current_path)
    yield FolderBeginEvent(current_path)

    sha1_hash = sha1()
    for item_name in sorted(os.listdir(folder_path)):
        next_path = '%s/%s' % (current_path, item_name)
        for evt in walk_item(base_path, next_path):
            sha1_hash.update(str(evt))
            yield evt

    checksum = sha1_hash.hexdigest()
    yield FolderEndEvent(current_path, checksum)

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
