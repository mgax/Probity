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
        out = sys.stdout.write
    else:
        out = lambda data: None

    for item in args:
        item_checksum = checksum.item_sha1(item, out)
        if not options.verbose:
            print '%s: %s' % (path.basename(item), item_checksum)
