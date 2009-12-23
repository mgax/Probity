import unittest
from StringIO import StringIO

from probity import compare

left_file_data = """\
[begin folder "root"]
[begin folder "bag"]
book: 3441943cc58015d62942d3ff1abffc256a4eda72
umbrella: d3d0d6f3991c664852ebb9c8945d9cb17ff00f7d
[begin folder "wallet"]
money: 59ef5096d34485ee0bc7b72136e911c5fb87ce23
[end folder "wallet": 91e11e366b932786a1714b9d82bd7babfb6823a7]
[end folder "bag": 5b4ed50250e736c39d822e4b987a95cf3b312c66]
[begin folder "box"]
ball: b5e1b2a54a67366c75d25634b1f8e6d6b2b5924b
[end folder "box": 45a56b922f7b829c594e58b3879b261bd337104b]
paper: 7c9aacf309179594a7106ad4a819c0e3bf509831
[end folder "root": 3bb2cf1ec8cd7d16c7fab448e6cb5f65786dd018]
"""

# left file structure:
#   root
#   root/bag
#   root/bag/book "red\n"
#   root/bag/umbrella "black\n"
#   root/bag/wallet
#   root/bag/wallet/money "green\n"
#   root/box
#   root/box/ball "blue\n"
#   root/paper "white\n"

def read_to_dict(data, skip_folders=False):
    output = dict()
    def handle(path, checksum, is_folder, **kwargs):
        if skip_folders and is_folder:
            return
        output[path] = checksum
    reader = compare.FileReader(handlers=[handle])
    reader.parse_file(StringIO(data))
    return output

class CompareTest(unittest.TestCase):
    def test_read_to_dict(self):
        output = read_to_dict(left_file_data)
        self.assertEqual(output['root'],
                         '3bb2cf1ec8cd7d16c7fab448e6cb5f65786dd018')
        self.assertEqual(output['root/bag'],
                         '5b4ed50250e736c39d822e4b987a95cf3b312c66')
        self.assertEqual(output['root/bag/book'],
                         '3441943cc58015d62942d3ff1abffc256a4eda72')
