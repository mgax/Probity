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
        os.mkdir(path.join(self.tmpdir, 'testf'))
        os.mkdir(path.join(self.tmpdir, 'testf/sub1'))
        os.mkdir(path.join(self.tmpdir, 'testf/sub1/sub2'))
        with open(path.join(self.tmpdir, 'testf/sub1/sub2/file1'), 'wb') as f:
            f.write('hello probity!')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_help(self):
        out, err = invoke_script(['-h'])
        self.assertEqual(err, '')
        self.assertTrue('Usage: probity' in out, (out,err))

    def test_checksum_file(self):
        file_path = path.join(self.tmpdir, 'testf/sub1/sub2/file1')
        out, err = invoke_script([file_path])
        self.assertEqual(err, '')
        self.assertEqual(out, 'file1: 6e28214b93900151eda8'
                                     '143c5605a5d084ee165c\n')

    def test_checksum_folder(self):
        out, err = invoke_script([path.join(self.tmpdir, 'testf')])
        self.assertEqual(err, '')
        self.assertEqual(out, 'testf: 47c14f38141d8fcb6e22'
                                          '09fbe990a7ddc102b2b2\n')

    def test_verbose(self):
        out, err = invoke_script(['-v', path.join(self.tmpdir, 'testf')])
        self.assertEqual(err, '')
        self.assertEqual(out,
                         ('[begin folder "testf"]\n'
                          '[begin folder "sub1"]\n'
                          '[begin folder "sub2"]\n'
                          'file1: 6e28214b93900151eda8143c5605a5d084ee165c\n'
                          '[end folder "sub2": '
                              '24c89cdebe9328b35a4afc43cdcbe5e38ab64c06]\n'
                          '[end folder "sub1": '
                              '55322dc65ff9ece08af84199b73000d3a9d80fa0]\n'
                          '[end folder "testf": '
                              '47c14f38141d8fcb6e2209fbe990a7ddc102b2b2]\n'))

    def test_verify(self):
        with open(path.join(self.tmpdir, 'old.prob'), 'w') as f:
            f.write('[begin folder "old"]\n'
                    'file_one: 6e28214b93900151eda8143c5605a5d084ee165c\n'
                    'file_two: 92f3bd369c2639c30e97d5163d4a8693928c411e\n'
                    '[end folder "old": '
                        'e897d8148ce4562021397535ae72f7d3b6752fa1]\n')
        testf_path = path.join(self.tmpdir, 'testf')
        old_prob_path = path.join(self.tmpdir, 'old.prob')
        out, err = invoke_script([testf_path, '--verify=' + old_prob_path])
        self.assertEqual(err, '')
        expected_out = ('Missing files:\n'
                        '  old/file_two: '
                            '92f3bd369c2639c30e97d5163d4a8693928c411e\n')
        self.assertTrue(expected_out in out)
