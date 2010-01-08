from hashlib import sha1
import os
from os import path

from probity import events

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
        return [events.FileEvent(base_path, current_path,
                                 file_sha1(item_path))]
    elif path.isdir(item_path):
        return walk_folder(base_path, current_path)
    else:
        raise NotImplementedError

def walk_folder(base_path, current_path):
    folder_path = path.join(base_path, current_path)
    yield events.FolderBeginEvent(current_path)

    sha1_hash = sha1()
    for item_name in sorted(os.listdir(folder_path)):
        next_path = '%s/%s' % (current_path, item_name)
        for evt in walk_item(base_path, next_path):
            sha1_hash.update(str(evt))
            yield evt

    checksum = sha1_hash.hexdigest()
    yield events.FolderEndEvent(current_path, checksum)
