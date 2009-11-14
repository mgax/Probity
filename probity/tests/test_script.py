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

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_help(self):
        out, err = invoke_script(['-h'])
        self.assertEqual(err, '')
        self.assertTrue('Usage: probity' in out, (out,err))
