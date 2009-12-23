import re

from probity import events

file_pattern = re.compile(r'^(?P<name>[^\:]+)\: (?P<checksum>[0-9a-f]{40})\n$')
begin_folder_pattern = re.compile(r'^\[begin folder "(?P<name>[^"]+)"\]\n$')
end_folder_pattern = re.compile(r'^\[end folder "(?P<name>[^"]+)"\: '
                                r'(?P<checksum>[0-9a-f]{40})\]\n$')

def parse_file(input_lines):
    stack = []
    current_path = lambda: '/'.join(stack + [name])

    for line in input_lines:
        file_match = file_pattern.match(line)
        if file_match is not None:
            name = file_match.group('name')
            checksum = file_match.group('checksum')
            yield events.FileEvent(current_path(), checksum)
            continue

        begin_folder_match = begin_folder_pattern.match(line)
        if begin_folder_match is not None:
            name = begin_folder_match.group('name')
            stack.append(name)
            yield events.FolderBeginEvent(current_path())
            continue

        end_folder_match = end_folder_pattern.match(line)
        if end_folder_match is not None:
            name = stack.pop()
            checksum = end_folder_match.group('checksum')
            assert name == end_folder_match.group('name')
            yield events.FolderEndEvent(current_path(), checksum)
            continue

        raise ValueError('Could not parse line: %r' % line)

    assert stack == [], "Truncated file"

def compare(reference, current_parser):
    reverse_reference = dict((v, k) for k, v in reference.iteritems())
    extra = set()

    for evt in current_parser:
        if evt.folder is not None:
            continue

        try:
            del reverse_reference[evt.checksum]
        except KeyError:
            extra.add(evt.path)

    missing = set(reverse_reference.itervalues())
    return {
        'missing': missing,
        'extra': extra,
    }
