import sys
from os import path
import optparse

from probity import walk
from probity import compare

option_parser = optparse.OptionParser()
option_parser.add_option("-v", "--verbose",
                         action="store_true", dest="verbose", default=False,
                         help="print hashes for all nested folders and files")
option_parser.add_option("-r", "--reference",
                         action="store", dest="reference_path",
                         help="verify against previous report")

def main():
    (options, args) = option_parser.parse_args()

    if options.reference_path is not None:
        reference = read_checksum_file(options.reference_path)
        comparator = compare.Comparator(reference)
    else:
        comparator = None

    for item in args:
        base_path, root_name = path.split(item)
        for evt in walk.walk_item(base_path, root_name):
            if options.verbose:
                sys.stdout.write(str(evt))
            if comparator is not None:
                comparator.update(evt)

        if not options.verbose:
            root_checksum = evt.checksum
            print '%s: %s' % (root_name, root_checksum)

    if comparator is not None:
        report = comparator.report()
        if report['missing']:
            print 'Missing files:'
            for file_path in report['missing']:
                print '  %s: %s' % (file_path, reference[file_path])

def read_checksum_file(file_path):
    data = dict()
    with open(file_path) as f:
        for evt in compare.parse_file(f):
            if evt.folder is None:
                data[evt.path] = evt.checksum
    return data
