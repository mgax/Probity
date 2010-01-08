import os
from os import path

from probity.walk import BLOCK_SIZE

class Backup(object):
    def __init__(self, pool_path):
        self.pool_path = pool_path

    def store_event(self, evt):
        if evt.folder is not None:
            return

        bucket_path = path.join(self.pool_path, evt.checksum[:2])
        file_path = path.join(bucket_path, evt.checksum[2:])

        if not path.isdir(bucket_path):
            os.makedirs(bucket_path)

        if not path.isfile(file_path):
            # TODO: use temporary file!
            with open(evt.fs_path, 'rb') as src_file:
                with open(file_path, 'wb') as dst_file:
                    while True:
                        data = src_file.read(BLOCK_SIZE)
                        if data:
                            dst_file.write(data)
                        else:
                            break
