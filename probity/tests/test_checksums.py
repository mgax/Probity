import unittest
import tempfile
import shutil
import os
from os import path
from StringIO import StringIO

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

    def test_folder_sha1(self):
        testfolder_path = path.join(self.tmpdir, 'testfolder')
        os.mkdir(testfolder_path)
        with open(path.join(testfolder_path, 'file1'), 'wb') as f:
            pass

        with open(path.join(testfolder_path, 'file2'), 'wb') as f:
            f.write('hello probity!')

        with open(path.join(testfolder_path, 'file3'), 'wb') as f:
            for c in xrange(1000):
                f.write('asdf' * 10)

        out = StringIO()
        sha1_digest = checksum.folder_sha1(testfolder_path, out)
        self.assertEqual(sha1_digest,
                         '3cc9b7a4af4e33050e5bbee1739a401f3922aa1f')
        self.assertEqual(out.getvalue(),
                         ('[begin folder "testfolder"]\n'
                          'file1: da39a3ee5e6b4b0d3255bfef95601890afd80709\n'
                          'file2: 6e28214b93900151eda8143c5605a5d084ee165c\n'
                          'file3: b3c791bfc591d5c7514c135465a484e4a0a3ae85\n'
                          '[end folder "testfolder": '
                              '3cc9b7a4af4e33050e5bbee1739a401f3922aa1f]\n'))

    def test_folder_recursive_sha1(self):
        testfolder_path = path.join(self.tmpdir, 'testfolder')
        os.mkdir(testfolder_path)
        os.mkdir(path.join(testfolder_path, 'sub1'))
        os.mkdir(path.join(testfolder_path, 'sub1/sub2'))
        with open(path.join(testfolder_path, 'sub1/sub2/file1'), 'wb') as f:
            f.write('hello probity!')

        out = StringIO()
        sha1_digest = checksum.folder_sha1(testfolder_path, out)
        self.assertEqual(sha1_digest,
                         '47c14f38141d8fcb6e2209fbe990a7ddc102b2b2')
        self.assertEqual(out.getvalue(),
                         ('[begin folder "testfolder"]\n'
                          '[begin folder "sub1"]\n'
                          '[begin folder "sub2"]\n'
                          'file1: 6e28214b93900151eda8143c5605a5d084ee165c\n'
                          '[end folder "sub2": '
                              '24c89cdebe9328b35a4afc43cdcbe5e38ab64c06]\n'
                          '[end folder "sub1": '
                              '55322dc65ff9ece08af84199b73000d3a9d80fa0]\n'
                          '[end folder "testfolder": '
                              '47c14f38141d8fcb6e2209fbe990a7ddc102b2b2]\n'))
