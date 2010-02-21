import sys
from os import path
import argparse

from probity import walk
from probity import compare
from probity import backup

def parse_probity_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="+",
        help="folder or file to be checksummed")
    parser.add_argument("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help="only print final checksum")
    parser.add_argument("-r", "--reference",
        action="store", dest="reference_path", metavar="REFERENCE_FILE",
        help="verify against previous report at REFERENCE_FILE")
    parser.add_argument("-b", "--backup",
        action="store", dest="backup_path", metavar="BACKUP_PATH",
        help="back up files to BACKUP_PATH")
    parser.add_argument("-i", "--interactive",
        action="store_true", dest="interactive", default=False,
        help="start a read-eval-print loop")
    return parser.parse_args()

def main():
    args = parse_probity_args()

    if args.reference_path is not None:
        reference = read_checksum_file(args.reference_path)
        comparator = compare.Comparator(reference)
    else:
        comparator = None

    if args.backup_path is not None:
        backup_pool = backup.Backup(args.backup_path)
    else:
        backup_pool = None

    if args.interactive:
        import code
        return code.interact("Probity interactive session", local=locals())

    for item in args.target:
        base_path, root_name = path.split(item)
        for evt in walk.walk_item(base_path, root_name):
            if not args.quiet:
                sys.stdout.write(str(evt))
            if comparator is not None:
                comparator.update(evt)
            if backup_pool is not None:
                backup_pool.store(evt)

        if args.quiet:
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
