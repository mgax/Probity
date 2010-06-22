import os
from os import path
import tempfile
from hashlib import sha1
from contextlib import contextmanager

from probity.walk import BLOCK_SIZE

class ChecksumWrapper(object):
    def __init__(self, orig_file):
        self.orig_file = orig_file
        self.sha1_hash = sha1()

    def write(self, data):
        self.orig_file.write(data)
        self.sha1_hash.update(data)

    def close(self):
        self.final_hash = self.sha1_hash.hexdigest()
        del self.sha1_hash

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

class Backup(object):
    def __init__(self, pool_path):
        self.pool_path = pool_path

    def store_event(self, evt):
        if evt.folder is not None:
            return

        if evt.checksum in self:
            return

        with open(evt.fs_path, 'rb') as src_file:
            with self.store_data(evt.checksum) as dst_file:
                while True:
                    data = src_file.read(BLOCK_SIZE)
                    if not data:
                        break
                    dst_file.write(data)

    @contextmanager
    def store_data(self, checksum):
        bucket_path = path.join(self.pool_path, checksum[:2])
        blob_path = path.join(bucket_path, checksum[2:])

        if not path.isdir(bucket_path):
            os.makedirs(bucket_path)

        fd, temp_path = tempfile.mkstemp(dir=self.pool_path)
        with os.fdopen(fd, 'wb') as temp_file:
            with ChecksumWrapper(temp_file) as wrapper:
                yield wrapper
            assert checksum == wrapper.final_hash

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
