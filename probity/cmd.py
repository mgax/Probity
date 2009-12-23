import sys
from os import path
import optparse

import checksum

option_parser = optparse.OptionParser()
option_parser.add_option("-v", "--verbose",
                         action="store_true", dest="verbose", default=False,
                         help="print hashes for all nested folders and files")

def main():
    (options, args) = option_parser.parse_args()

    if options.verbose:
        handle = sys.stdout.write
    else:
        handle = lambda evt: None

    for item in args:
        base_path, root_name = path.split(item)
        item_checksum = checksum.item_sha1(base_path, root_name, handle)
        if not options.verbose:
            print '%s: %s' % (root_name, item_checksum)
