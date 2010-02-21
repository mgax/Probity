import unittest
import tempfile
import shutil
import sys
import os
from os import path
from StringIO import StringIO
import yaml

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
        self.assertTrue('usage: probity' in err, (out,err))
        self.assertEqual(out, '')

    def test_checksum_file(self):
        file_path = path.join(self.tmpdir, 'testf/sub1/sub2/file1')
        out, err = invoke_script(['checksum', file_path])
        self.assertEqual(err, '')
        out_data = yaml.load(out)
        self.assertEqual(out_data.keys(), ['file1'])
        self.assertEqual(out_data['file1']['sha1'],
                         '6e28214b93900151eda8143c5605a5d084ee165c')
        self.assertEqual(out_data['file1']['size'], 14)

    def test_checksum_folder(self):
        out, err = invoke_script(['checksum', '-q',
                                  path.join(self.tmpdir, 'testf')])
        self.assertEqual(err, '')
        self.assertEqual(out, 'testf: 47c14f38141d8fcb6e22'
                                          '09fbe990a7ddc102b2b2\n')

    def test_verbose(self):
        out, err = invoke_script(['checksum', path.join(self.tmpdir, 'testf')])
        self.assertEqual(err, '')
        out_data = yaml.load(out)
        self.assertEqual(out_data.keys(), ['testf/sub1/sub2/file1'])
        self.assertEqual(out_data['testf/sub1/sub2/file1']['sha1'],
                         '6e28214b93900151eda8143c5605a5d084ee165c')
        self.assertEqual(out_data['testf/sub1/sub2/file1']['size'], 14)

    def test_verify(self):
        with open(path.join(self.tmpdir, 'old.prob'), 'w') as f:
            f.write('[begin folder "old"]\n'
                    'file_one: 6e28214b93900151eda8143c5605a5d084ee165c\n'
                    'file_two: 92f3bd369c2639c30e97d5163d4a8693928c411e\n'
                    '[end folder "old": '
                        'e897d8148ce4562021397535ae72f7d3b6752fa1]\n')
        testf_path = path.join(self.tmpdir, 'testf')
        old_prob_path = path.join(self.tmpdir, 'old.prob')
        out, err = invoke_script(['verify', testf_path,
                                  '--reference=' + old_prob_path])
        self.assertEqual(err, '')
        expected_out = ('Missing files:\n'
                        '  old/file_two: '
                            '92f3bd369c2639c30e97d5163d4a8693928c411e\n')
        self.assertTrue(expected_out in out, out)

    def test_backup(self):
        out, err = invoke_script(['backup', path.join(self.tmpdir, 'testf'),
                                  '-b', path.join(self.tmpdir, 'backup')])
        self.assertEqual(err, '')
        self.assertEqual(out, 'testf: 47c14f38141d8fcb6e22'
                                          '09fbe990a7ddc102b2b2\n')
        self.assertEqual(os.listdir(path.join(self.tmpdir, 'backup')), ['6e'])
        with open(path.join(self.tmpdir, 'backup', '6e',
                  '28214b93900151eda8143c5605a5d084ee165c'), 'rb') as f:
            self.assertEqual(f.read(), 'hello probity!')

class CompareTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        with open(self.tmpdir + '/left.prob', 'wb') as f:
            f.write('some_file_1: {size: 754368, sha1: '
                            'a7e26aec552842dadf0345c6af7dbafd91eb4788}\n')
            f.write('some_file_2: {size: 773093, sha1: '
                            'c7c9598a4ea55eedf59c69b94683fa4ff3581bba}\n')
        with open(self.tmpdir + '/right.prob', 'wb') as f:
            f.write('some_file_3: {size: 754368, sha1: '
                            'a7e26aec552842dadf0345c6af7dbafd91eb4788}\n')
            f.write('some_file_4: {size: 2941132, sha1: '
                            '945da7c5249f47ea5a4de6fe013c93908c53c10c}\n')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_compare(self):
        left_path = path.join(self.tmpdir, 'left.prob')
        right_path = path.join(self.tmpdir, 'right.prob')
        out, err = invoke_script(['compare', left_path, right_path])

        assert err == ''
        assert out == ('Removed files:\n'
                       '  some_file_2\n'
                       'Added files:\n'
                       '  some_file_4\n')
