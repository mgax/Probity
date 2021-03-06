import re

import yaml
import yaml.events
import yaml.dumper

from probity import events

class YamlStreamReader(object):
    def __init__(self, stream):
        self.loader = yaml.Loader(stream)

    def _skip(self, event_type, raise_on_error=True):
        event = self.loader.get_event()
        if not isinstance(event, event_type):
            if raise_on_error:
                raise AssertionError('Malformed input steam')
            else:
                print "Error in input stream"

    def __enter__(self):
        self._skip(yaml.events.StreamStartEvent)
        self._skip(yaml.events.DocumentStartEvent)
        self._skip(yaml.events.MappingStartEvent)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            return
        self._skip(yaml.events.MappingEndEvent, False)
        self._skip(yaml.events.DocumentEndEvent, False)
        self._skip(yaml.events.StreamEndEvent, False)

    def __iter__(self):
        return self

    def next(self):
        l = self.loader
        if l.check_event(yaml.events.MappingEndEvent):
            raise StopIteration
        key = l.construct_object(l.compose_node(None, None))
        value = l.construct_object(l.compose_node(None, None),
                                        deep=True)
        return key, value

def parse_yaml(stream):
    with YamlStreamReader(stream) as reader:
        for key, value in reader:
            yield events.FileEvent('_yamlfile', key,
                                   value['sha1'], value['size'])

file_pattern = re.compile(r'^(?P<name>[^\:]+)\: (?P<checksum>[0-9a-f]{40})\n$')
begin_folder_pattern = re.compile(r'^\[begin folder "(?P<name>[^"]+)"\]\n$')
end_folder_pattern = re.compile(r'^\[end folder "(?P<name>[^"]+)"\: '
                                r'(?P<checksum>[0-9a-f]{40})\]\n$')
def parse_old_format(input_lines):
    stack = []
    current_path = lambda: '/'.join(stack + [name])

    for line in input_lines:
        file_match = file_pattern.match(line)
        if file_match is not None:
            name = file_match.group('name')
            checksum = file_match.group('checksum')
            yield events.FileEvent('', current_path(), checksum)
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

def parse_file(stream):
    assert stream.tell() == 0
    ch1 = stream.read(1)
    stream.seek(0)
    if ch1 == '[':
        return parse_old_format(stream)
    else:
        return parse_yaml(stream)

class YamlDumper(object):
    def __init__(self, stream):
        self.dumper = yaml.dumper.Dumper(stream)

    def __enter__(self):
        self.dumper.open()
        self.dumper.emit(yaml.events.DocumentStartEvent())
        self.dumper.emit(yaml.events.MappingStartEvent(anchor=None, tag=None,
                                                       implicit=True))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            return
        self.dumper.emit(yaml.events.MappingEndEvent())
        self.dumper.emit(yaml.events.DocumentEndEvent())
        self.dumper.close()

    def _write_data(self, data):
        node = self.dumper.represent_data(data)
        self.dumper.anchor_node(node)
        self.dumper.serialize_node(node, None, None)

    def write(self, evt):
        self._write_data(evt.path)
        self._write_data({'sha1': evt.checksum, 'size': evt.size})
