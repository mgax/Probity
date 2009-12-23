from hashlib import sha1
import os
from os import path

def file_sha1(file_path):
    sha1_hash = sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1_hash.update(data)
    return sha1_hash.hexdigest()

def item_sha1(item_path, out):
    if path.isfile(item_path):
        item_checksum = file_sha1(item_path)
        item_name = path.basename(item_path)
        item_line = '%s: %s\n' % (item_name, item_checksum)
        out(item_line)
    elif path.isdir(item_path):
        item_checksum = folder_sha1(item_path, out)
    else:
        raise NotImplementedError

    return item_checksum

def folder_sha1(folder_path, out):
    if not callable(out):
        # assume it's a file-like object
        out = out.write

    folder_name = path.basename(folder_path)
    out('[begin folder "%s"]\n' % folder_name)

    sha1_hash = sha1()
    def my_out(data):
        " the magic of lisp :) "
        out(data)
        sha1_hash.update(data)

    for item_name in sorted(os.listdir(folder_path)):
        item_path = path.join(folder_path, item_name)
        item_sha1(item_path, my_out)

    sha1_digest = sha1_hash.hexdigest()
    out('[end folder "%s": %s]\n' % (folder_name, sha1_digest))

    return sha1_digest
