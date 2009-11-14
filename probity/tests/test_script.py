import unittest
import tempfile
import shutil
import sys
import os
from os import path
from StringIO import StringIO

from probity import cmd

def invoke_script(args):
    orig_sys = {}
    for name in ('argv', 'stdout', 'stderr'):
        orig_sys[name] = getattr(sys, name)

    sys.argv = ['probity'] + args
    sys.stdout = stdout = StringIO()
    sys.stderr = stderr = StringIO()

    try:
        cmd.main()
    except SystemExit:
        pass
    finally:
        out = stdout.getvalue()
        err = stderr.getvalue()
        for name, value in orig_sys.items():
            setattr(sys, name, value)

    return out, err

class InvokeScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        testfolder_path = path.join(self.tmpdir, 'testfolder')
        os.mkdir(testfolder_path)
        os.mkdir(path.join(testfolder_path, 'sub1'))
        os.mkdir(path.join(testfolder_path, 'sub1/sub2'))
        with open(path.join(testfolder_path, 'sub1/sub2/file1'), 'wb') as f:
            f.write('hello probity!')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_help(self):
        out, err = invoke_script(['-h'])
        self.assertEqual(err, '')
        self.assertTrue('Usage: probity' in out, (out,err))

    def test_checksum_file(self):
        file_path = path.join(self.tmpdir, 'testfolder/sub1/sub2/file1')
        out, err = invoke_script([file_path])
        self.assertEqual(err, '')
        self.assertEqual(out, 'file1: 6e28214b93900151eda8'
                                     '143c5605a5d084ee165c\n')

    def test_checksum_folder(self):
        file_path = path.join(self.tmpdir, 'testfolder')
        out, err = invoke_script([file_path])
        self.assertEqual(err, '')
        self.assertEqual(out, 'testfolder: 47c14f38141d8fcb6e22'
                                          '09fbe990a7ddc102b2b2\n')
