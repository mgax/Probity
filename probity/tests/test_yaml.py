import unittest
from StringIO import StringIO

import yaml

from probity import events
from probity import probfile

testfile_yaml = """\
somefile: {sha1: 'da39a3ee5e6b4b0d3255bfef95601890afd80709', size: 0}
fol/otherfile: {sha1: '6e28214b93900151eda8143c5605a5d084ee165c', size: 14}
"""

def test_yaml_raw_parser():
    value1 = {'sha1': 'da39a3ee5e6b4b0d3255bfef95601890afd80709', 'size': 0}
    value2 = {'sha1': '6e28214b93900151eda8143c5605a5d084ee165c', 'size': 14}

    raw_parser = probfile.YamlStreamReader(StringIO(testfile_yaml))
    raw_parser.__enter__()

    assert raw_parser.next() == ('somefile', value1)
    assert raw_parser.next() == ('fol/otherfile', value2)

    assert_raises(StopIteration, raw_parser.next)
    raw_parser.__exit__(None, None, None)

def test_parse_yaml():
    parser = probfile.parse_yaml(StringIO(testfile_yaml))

    evt1 = next(parser)
    assert evt1.path == 'somefile'
    assert evt1.checksum == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert evt1.size == 0

    evt2 = next(parser)
    assert evt2.path == 'fol/otherfile'
    assert evt2.checksum == '6e28214b93900151eda8143c5605a5d084ee165c'
    assert evt2.size == 14

    assert_raises(StopIteration, parser.next)

def test_dump_yaml():
    evt1 = events.FileEvent('', 'somefile',
                            'da39a3ee5e6b4b0d3255bfef95601890afd80709', 0)
    evt2 = events.FileEvent('', 'fol/otherfile',
                            '6e28214b93900151eda8143c5605a5d084ee165c', 14)
    reference_output = {
        'somefile': {'sha1': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                     'size': 0},
        'fol/otherfile': {'sha1': '6e28214b93900151eda8143c5605a5d084ee165c',
                          'size': 14},
    }

    out_file = StringIO()
    with probfile.YamlDumper(out_file) as dumper:
        dumper.write(evt1)
        dumper.write(evt2)

    out_file.seek(0)
    assert yaml.load(out_file) == reference_output

def assert_raises(exc, callback):
    try:
        callback()
    except exc:
        pass
    else:
        raise AssertionError('%r did not raise %r' % (callback, exc))
