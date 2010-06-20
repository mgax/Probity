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

        if evt.checksum not in self:
            with open(evt.fs_path, 'rb') as src_file:
                self.store_data(evt.checksum, src_file)

    def store_data(self, checksum, src_file):
        bucket_path = path.join(self.pool_path, checksum[:2])
        blob_path = path.join(bucket_path, checksum[2:])

        if not path.isdir(bucket_path):
            os.makedirs(bucket_path)

        temp_path = tempfile.mkstemp(dir=self.pool_path)[1]
        with open(temp_path, 'wb') as temp_file:
            while True:
                data = src_file.read(BLOCK_SIZE)
                if not data:
                    break

                temp_file.write(data)

        os.rename(temp_path, blob_path)

    def open_data(self, checksum):
        # TODO: write tests for this method
        bucket_path = path.join(self.pool_path, checksum[:2])
        blob_path = path.join(bucket_path, checksum[2:])
        assert path.isfile(blob_path)
        return open(blob_path, 'rb')

    def __contains__(self, checksum):
        assert isinstance(checksum, str)
        assert len(checksum) == 40
        hash_path = path.join(self.pool_path, checksum[:2], checksum[2:])
        return path.isfile(hash_path)
