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
            final_evt = do_checksum(args.target)
            print '%s: %s' % (final_evt.name, final_evt.checksum)
        else:
            with probfile.YamlDumper(sys.stdout) as output:
                do_checksum(args.target, output.write)

    elif args.subcmd == 'backup':
        do_checksum(args.target, backup.Backup(args.backup_path).store)

    elif args.subcmd == 'verify':
        reference = read_checksum_file(args.reference_path)
        comparator = compare.Comparator(reference)
        do_checksum(args.target, comparator.update)
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

def do_checksum(target_path, *event_handlers):
    base_path, root_name = path.split(target_path)
    for evt in walk.walk_item(base_path, root_name):
        if evt.folder is None:
            for handler in event_handlers:
                handler(evt)
    return evt # the final event, with checksum for the whole folder

def read_checksum_file(file_path):
    data = dict()
    with open(file_path) as f:
        for evt in probfile.parse_file(f):
            if evt.folder is None:
                data[evt.path] = evt.checksum
    return data
