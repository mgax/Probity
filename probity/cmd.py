import sys
from os import path
import optparse

import checksum

def main():
    parser = optparse.OptionParser()
    (options, args) = parser.parse_args()
    for item in args:
        item_checksum = checksum.item_sha1(item, lambda data: None)
        print '%s: %s' % (path.basename(item), item_checksum)
