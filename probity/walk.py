from hashlib import sha1
import os
from os import path

from probity import events

BLOCK_SIZE = 65536

def file_sha1_and_size(file_path):
    sha1_hash = sha1()
    size = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break
            sha1_hash.update(data)
            size += len(data)
    return sha1_hash.hexdigest(), size

def step_item(base_path, current_path):
    item_path = path.join(base_path, current_path)
    if path.isfile(item_path):
        checksum, size = file_sha1_and_size(item_path)
        return [events.FileEvent(base_path, current_path, checksum, size)]
    elif path.isdir(item_path):
        return step_folder(base_path, current_path)
    else:
        raise NotImplementedError

def step_folder(base_path, current_path):
    folder_path = path.join(base_path, current_path)
    yield events.FolderBeginEvent(current_path)

    sha1_hash = sha1()
    for item_name in sorted(os.listdir(folder_path)):
        next_path = '%s/%s' % (current_path, item_name)
        for evt in step_item(base_path, next_path):
            sha1_hash.update(str(evt))
            yield evt

    checksum = sha1_hash.hexdigest()
    yield events.FolderEndEvent(current_path, checksum)

def walk_path(target_path, handle_final=None):
    """
    Yields events for files in `target_path` (but not folders).
    If `handle_final` is not None, it gets called with the event
    for the root object (usually a foler) as single argument.
    """
    base_path, root_name = path.split(target_path)

    for evt in step_item(base_path, root_name):
        if evt.folder is None:
            yield evt

    if handle_final is not None:
        handle_final(evt)
