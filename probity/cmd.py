import sys
from os import path
import argparse

from probity import walk
from probity import compare
from probity import backup
from probity import probfile

def parse_probity_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcmd')

    checksum_parser = subparsers.add_parser('checksum',
        help="calculate the checksum of a folder")
    checksum_parser.add_argument("target", help="folder to be checksummed")
    checksum_parser.add_argument("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help="only print final checksum")

    backup_parser = subparsers.add_parser('backup',
        help="Back up a folder to a hashed filesystem repository")
    backup_parser.add_argument("target", help="folder to be checksummed")
    backup_parser.add_argument("-b", "--backup",
        action="store", dest="backup_path", metavar="BACKUP_PATH",
        help="back up files to BACKUP_PATH")

    verify_parser = subparsers.add_parser('verify',
        help="Verify the contents of a given folder against a report file")
    verify_parser.add_argument("target", help="folder to be checksummed")
    verify_parser.add_argument("-r", "--reference",
        action="store", dest="reference_path", metavar="REFERENCE_FILE",
        help="verify against previous report at REFERENCE_FILE")

    compare_parser = subparsers.add_parser('compare',
        help="Compare two probity reports")
    compare_parser.add_argument("left", help="the 'original' report")
    compare_parser.add_argument("right", help="the 'new' report")

    interact_parser = subparsers.add_parser('interact',
        help="start a read-eval-print loop")

    return parser.parse_args()

def main():
    args = parse_probity_args()

    if args.subcmd == 'checksum':
        if args.quiet:
            def handle_final(evt):
                print '%s: %s' % (evt.name, evt.checksum)
            for evt in walk.walk_path(args.target, handle_final):
                pass
        else:
            with probfile.YamlDumper(sys.stdout) as output:
                for evt in walk.walk_path(args.target):
                    output.write(evt)

    elif args.subcmd == 'backup':
        backup_pool = backup.Backup(args.backup_path)
        for evt in walk.walk_path(args.target):
            backup_pool.store(evt)

    elif args.subcmd == 'verify':
        reference = read_checksum_file(args.reference_path)
        comparator = compare.Comparator(reference)
        for evt in walk.walk_path(args.target):
            comparator.update(evt)
        report = comparator.report()
        if report['missing']:
            print 'Missing files:'
            for file_path in report['missing']:
                print '  %s: %s' % (file_path, reference[file_path])

    elif args.subcmd == 'compare':
        reference = read_checksum_file(args.left)
        comparator = compare.Comparator(reference)
        with open(args.right, 'rb') as right_file:
            for evt in probfile.parse_file(right_file):
                comparator.update(evt)

        report = comparator.report()

        if report['missing']:
            print 'Removed files:'
            for file_path in report['missing']:
                print '  %s' % (file_path)

        if report['extra']:
            print 'Added files:'
            for file_path in report['extra']:
                print '  %s' % (file_path)

    elif args.subcmd == 'interact':
        import code
        return code.interact("Probity interactive session", local=locals())

    else:
        raise NotImplementedError

def read_checksum_file(file_path):
    data = dict()
    with open(file_path) as f:
        for evt in probfile.parse_file(f):
            if evt.folder is None:
                data[evt.path] = evt.checksum
    return data
