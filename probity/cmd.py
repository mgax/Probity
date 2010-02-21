import sys
from os import path
import argparse

from probity import walk
from probity import compare
from probity import backup

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

    interact_parser = subparsers.add_parser('interact',
        help="start a read-eval-print loop")

    return parser.parse_args()

def main():
    args = parse_probity_args()

    if args.subcmd == 'checksum':
        do_checksum(args.target, print_all=(not args.quiet))

    elif args.subcmd == 'backup':
        do_checksum(args.target, backup_pool=backup.Backup(args.backup_path))

    elif args.subcmd == 'verify':
        reference = read_checksum_file(args.reference_path)
        comparator = compare.Comparator(reference)
        do_checksum(args.target, comparator=comparator)
        report = comparator.report()
        if report['missing']:
            print 'Missing files:'
            for file_path in report['missing']:
                print '  %s: %s' % (file_path, reference[file_path])

    elif args.subcmd == 'interact':
        import code
        return code.interact("Probity interactive session", local=locals())

    else:
        raise NotImplementedError

def do_checksum(target_path, print_all=False,
                backup_pool=None, comparator=None):
    base_path, root_name = path.split(target_path)
    for evt in walk.walk_item(base_path, root_name):
        if print_all:
            sys.stdout.write(str(evt))
        if comparator is not None:
            comparator.update(evt)
        if backup_pool is not None:
            backup_pool.store(evt)

    if not print_all:
        root_checksum = evt.checksum
        print '%s: %s' % (root_name, root_checksum)

def read_checksum_file(file_path):
    data = dict()
    with open(file_path) as f:
        for evt in compare.parse_file(f):
            if evt.folder is None:
                data[evt.path] = evt.checksum
    return data
