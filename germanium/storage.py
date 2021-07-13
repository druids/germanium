import os

from io import StringIO, BytesIO
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri, force_bytes
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.encoding import filepath_to_uri
from django.utils import timezone

from collections import defaultdict


class PathDoesNotExist(Exception):
    pass


class InMemoryNode:
    """
    Base class for files and directories.
    """
    parent = None

    def add_child(self, name, child):
        child.parent = self
        self.children[name] = child


class InMemoryFile(InMemoryNode, File):
    """
    Stores contents of file and stores reference to parent. File interface is identical
    to ContentFile, except that self.size works even after data has been written to it
    """
    def __init__(self, content='', parent=None, name=None):
        #init InMemoryNode
        self.parent = parent
        self.created_at = timezone.now()
        self.last_modified = timezone.now()
        self.last_accessed = timezone.now()

        stream_class = StringIO if isinstance(content, str) else BytesIO
        File.__init__(self, stream_class(content), name=name)

    def __str__(self):
        return '<InMemoryFile: %s>' % self.name

    def __bool__(self):
        return True

    def __nonzero__(self):      # Python 2 compatibility
        return type(self).__bool__(self)

    @property
    def _size(self):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(pos)
        return size

    def open(self, mode=None):
        self.seek(0)
        if 'b' in mode:
            if not isinstance(self.file, BytesIO):
                self.file = BytesIO(self.file.getvalue().encode('utf-8'))
        else:
            if not isinstance(self.file, StringIO):
                self.file = StringIO(self.file.getvalue().decode('utf-8'))

    def close(self):
        pass


class InMemoryDir(InMemoryNode):
    """
    Stores dictionary of child directories/files and reference to parent.
    """
    def __init__(self, dirs=None, files=None, parent=None):
        self.children = {}
        self.parent = parent

    def resolve(self, path, create=False, use_bytes=False):
        path = os.path.normpath(path)
        path_bits = path.strip(os.sep).split(os.sep, 1)
        current = path_bits[0]
        rest = path_bits[1] if len(path_bits) > 1 else None
        if not rest:
            if current == '.' or current == '':
                return self
            if current in self.children.keys():
                return self.children[current]
            if not create:
                raise PathDoesNotExist(path)
            content = b'' if use_bytes else ''
            node = InMemoryFile(name=current, content=content)
            self.add_child(current, node)
            return node
        if current in self.children.keys():
            return self.children[current].resolve(rest, create=create, use_bytes=use_bytes)
        if not create:
            raise PathDoesNotExist(path)
        node = InMemoryDir()
        self.add_child(current, node)
        return self.children[current].resolve(rest, create=create, use_bytes=use_bytes)

    def ls(self, path=''):
        return list(self.resolve(path).children.keys())

    def listdir(self, dir):
        nodes = tuple(self.resolve(dir).children.items())
        dirs = [k for (k, v) in nodes if isinstance(v, InMemoryDir)]
        files = [k for (k, v) in nodes if isinstance(v, InMemoryFile)]
        return [dirs, files]

    def delete(self, path):
        node = self.resolve(path)
        for name, child in node.parent.children.items():
            if child is node:
                del node.parent.children[name]
                break

    def exists(self, name):
        try:
            self.resolve(name)
        except PathDoesNotExist:
            return False
        else:
            return True

    def size(self, name):
        return self.resolve(name).size

    def open(self, path, mode="r"):
        create = "w" in mode
        use_bytes = "b" in mode
        f = self.resolve(path, create=create, use_bytes=use_bytes)
        f.open(mode)
        f.last_accessed = timezone.now()
        return f

    def save(self, path, content):
        mode = 'wb' if isinstance(content, bytes) else 'w'
        with self.open(path, mode) as f:
            f.write(content)
        f.last_modified = timezone.now()
        return path


test_filesystems = defaultdict(lambda: defaultdict(InMemoryDir))


@deconstructible
class TestInMemoryStorage(Storage):
    """
    Django storage class for in-memory filesystem.
    """

    filesystem_name = 'default'

    def __init__(self, base_url=None):
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.base_url = base_url

    @property
    def filesystem(self):
        return test_filesystems[os.getpid()][self.filesystem_name]

    def listdir(self, dir):
        return self.filesystem.listdir(dir)

    def delete(self, path):
        return self.filesystem.delete(path)

    def exists(self, name):
        return self.filesystem.exists(name)

    def size(self, name):
        return self.filesystem.size(name)

    def _open(self, name, mode="r"):
        return self.filesystem.open(name, mode)

    def _save(self, name, content):
        return self.filesystem.save(name, content.read())

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urljoin(self.base_url, filepath_to_uri(name))

    def modified_time(self, name):
        file = self.filesystem.resolve(name)
        return file.last_modified

    def accessed_time(self, name):
        file = self.filesystem.resolve(name)
        return file.last_accessed

    def created_time(self, name):
        file = self.filesystem.resolve(name)
        return file.created_at

    def __eq__(self, other):
        return self.filesystem == other.filesystem and self.base_url == other.base_url
