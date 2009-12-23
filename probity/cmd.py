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

    for item in args:
        base_path, root_name = path.split(item)
        for evt in checksum.walk_item(base_path, root_name):
            if options.verbose:
                sys.stdout.write(evt)

        if not options.verbose:
            # `evt` is the final event
            print '%s: %s' % (root_name, evt.checksum)
