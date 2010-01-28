import sys
from os import path
import optparse

from probity import walk
from probity import compare
from probity import backup

option_parser = optparse.OptionParser()
option_parser.add_option("-q", "--quiet",
    action="store_true", dest="quiet", default=False,
    help="only print final checksum")
option_parser.add_option("-r", "--reference",
    action="store", dest="reference_path", metavar="REFERENCE_FILE",
    help="verify against previous report at REFERENCE_FILE")
option_parser.add_option("-b", "--backup",
    action="store", dest="backup_path", metavar="BACKUP_PATH",
    help="back up files to BACKUP_PATH")
option_parser.add_option("-i", "--interactive",
    action="store_true", dest="interactive", default=False,
    help="start a read-eval-print loop")

def main():
    (options, args) = option_parser.parse_args()

    if options.reference_path is not None:
        reference = read_checksum_file(options.reference_path)
        comparator = compare.Comparator(reference)
    else:
        comparator = None

    if options.backup_path is not None:
        backup_pool = backup.Backup(options.backup_path)
    else:
        backup_pool = None

    if options.interactive:
        import code
        return code.interact("Probity interactive session", local=locals())

    for item in args:
        base_path, root_name = path.split(item)
        for evt in walk.walk_item(base_path, root_name):
            if not options.quiet:
                sys.stdout.write(str(evt))
            if comparator is not None:
                comparator.update(evt)
            if backup_pool is not None:
                backup_pool.store(evt)

        if options.quiet:
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
