from hashlib import sha1
from StringIO import StringIO
import os
from os import path

def file_sha1(file_path):
    sha1_hash = sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha1_hash.update(data)
    return sha1_hash.hexdigest()

def folder_sha1(folder_path):
    out = StringIO()
    folder_name = path.basename(folder_path)
    print>>out, '[begin folder "%s"]' % folder_name
    for file_name in sorted(os.listdir(folder_path)):
        file_checksum = file_sha1(path.join(folder_path, file_name))
        print>>out, '%s:' % file_name, file_checksum
    print>>out, '[end folder "%s"]' % folder_name
    return out.getvalue()
