import unittest
import tempfile
import shutil
import os
from os import path

from probity import walk
from probity import backup

class BackupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.mkdir(path.join(self.tmpdir, 'data'))
        os.mkdir(path.join(self.tmpdir, 'data/dirA'))
        with open(path.join(self.tmpdir, 'data/dirA/f1'), 'wb') as f:
            f.write('file one')
        with open(path.join(self.tmpdir, 'data/dirA/f2'), 'wb') as f:
            f.write('file two')
        with open(path.join(self.tmpdir, 'data/f3'), 'wb') as f:
            f.write('file three')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_backup(self):
        backup_path = path.join(self.tmpdir, 'backup')

        test_backup = backup.Backup(backup_path)
        for evt in walk.step_item(self.tmpdir, 'data'):
            test_backup.store_event(evt)

        f1_sha = '62', 'a837970950bf34fb0c401c39cd3c0d373f0a7a'
        f2_sha = 'e8', 'c3c333536348ba9c1822930ace36c506ef168d'
        f3_sha = '1d', 'e35ef0e3d36a9a753e459a9471fae8b909f048'
        self.assertEqual(set(os.listdir(backup_path)),
                         set([f1_sha[0], f2_sha[0], f3_sha[0]]))

        self.assertEqual(os.listdir(path.join(backup_path, f1_sha[0])),
                         [f1_sha[1]])
        with open(path.join(backup_path, f1_sha[0], f1_sha[1]), 'rb') as f:
            self.assertEqual(f.read(), 'file one')

        self.assertEqual(os.listdir(path.join(backup_path, f2_sha[0])),
                         [f2_sha[1]])
        with open(path.join(backup_path, f2_sha[0], f2_sha[1]), 'rb') as f:
            self.assertEqual(f.read(), 'file two')

        self.assertEqual(os.listdir(path.join(backup_path, f3_sha[0])),
                         [f3_sha[1]])
        with open(path.join(backup_path, f3_sha[0], f3_sha[1]), 'rb') as f:
            self.assertEqual(f.read(), 'file three')

    def test_backup_skip_existing(self):
        backup_path = path.join(self.tmpdir, 'backup')

        f2_sha = 'e8', 'c3c333536348ba9c1822930ace36c506ef168d'
        os.makedirs(path.join(backup_path, f2_sha[0]))
        with open(path.join(backup_path, f2_sha[0], f2_sha[1]), 'wb') as f:
            f.write('something else')

        test_backup = backup.Backup(backup_path)
        for evt in walk.step_item(self.tmpdir, 'data'):
            test_backup.store_event(evt)

        with open(path.join(backup_path, f2_sha[0], f2_sha[1]), 'rb') as f:
            self.assertEqual(f.read(), 'something else')

    def test_backup_contains(self):
        backup_path = path.join(self.tmpdir, 'backup')
        test_backup = backup.Backup(backup_path)
        for evt in walk.step_item(self.tmpdir, 'data'):
            test_backup.store_event(evt)

        self.assertTrue('62a837970950bf34fb0c'
                        '401c39cd3c0d373f0a7a' in test_backup)
        self.assertTrue('62a837970950bf34fb0c'
                        '00000000000000000000' not in test_backup)
