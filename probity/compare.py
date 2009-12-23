import re

file_pattern = re.compile(r'^(?P<name>[^\:]+)\: (?P<checksum>[0-9a-f]{40})\n$')
begin_folder_pattern = re.compile(r'^\[begin folder "(?P<name>[^"]+)"\]\n$')
end_folder_pattern = re.compile(r'^\[end folder "(?P<name>[^"]+)"\: '
                                r'(?P<checksum>[0-9a-f]{40})\]\n$')

class FileReader(object):
    def __init__(self, handlers):
        self.handlers = handlers

    def parse_file(self, f):
        stack = []

        def send(name, checksum, folder=None):
            kwargs = {
                'name': name,
                'path': '/'.join(stack + [name]),
                'folder': folder,
                'checksum': None,
            }
            if folder != 'begin':
                kwargs['checksum'] = checksum

            for handler in self.handlers:
                handler(**kwargs)

        for line in f:
            file_match = file_pattern.match(line)
            if file_match is not None:
                name = file_match.group('name')
                send(name, file_match.group('checksum'))
                continue

            begin_folder_match = begin_folder_pattern.match(line)
            if begin_folder_match is not None:
                name = begin_folder_match.group('name')
                stack.append(name)
                send(name, None, folder='begin')
                continue

            end_folder_match = end_folder_pattern.match(line)
            if end_folder_match is not None:
                name = stack.pop()
                assert name == end_folder_match.group('name')
                send(name, end_folder_match.group('checksum'), folder='end')
                continue

            raise ValueError('Could not parse line: %r' % line)

        assert stack == [], "Truncated file"

class ChecksumComparator(object):
    def __init__(self, reference):
        self.reference = reference
        self.reverse_reference = dict((v, k) for k, v in reference.iteritems())
        self.extra = set()

    def handle(self, path, checksum, folder, **kwargs):
        if folder is not None:
            return
        try:
            del self.reverse_reference[checksum]
        except KeyError:
            self.extra.add(path)

    def report(self):
        missing = set(self.reverse_reference.itervalues())
        return {
            'missing': missing,
            'extra': self.extra,
        }
