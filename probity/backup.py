import os
from os import path
import tempfile

from probity.walk import BLOCK_SIZE

class Backup(object):
    def __init__(self, pool_path):
        self.pool_path = pool_path

    def store_event(self, evt):
        if evt.folder is not None:
            return

        bucket_path = path.join(self.pool_path, evt.checksum[:2])
        blob_path = path.join(bucket_path, evt.checksum[2:])

        if not path.isdir(bucket_path):
            os.makedirs(bucket_path)

        if not path.isfile(blob_path):
            # TODO: use temporary file!
            temp_path = tempfile.mkstemp(dir=self.pool_path)[1]
            with open(temp_path, 'wb') as temp_file:
                with open(evt.fs_path, 'rb') as src_file:
                    while True:
                        data = src_file.read(BLOCK_SIZE)
                        if data:
                            temp_file.write(data)
                        else:
                            break
            os.rename(temp_path, blob_path)
