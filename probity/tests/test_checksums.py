import unittest
import tempfile
import shutil
from os import path

from probity import checksum

class ChecksumsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_file_sha1(self):
        testfile_path = path.join(self.tmpdir, 'testfile')

        # blank file
        with open(testfile_path, 'wb') as f:
            pass
        self.assertEqual(checksum.file_sha1(testfile_path),
                         'da39a3ee5e6b4b0d3255bfef95601890afd80709')

        # short text
        with open(testfile_path, 'wb') as f:
            f.write('hello probity!')
        self.assertEqual(checksum.file_sha1(testfile_path),
                         '6e28214b93900151eda8143c5605a5d084ee165c')

        # 40KB text
        with open(testfile_path, 'wb') as f:
            for c in xrange(1000):
                f.write('asdf' * 10)
        self.assertEqual(checksum.file_sha1(testfile_path),
                         'b3c791bfc591d5c7514c135465a484e4a0a3ae85')
