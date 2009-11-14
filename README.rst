Probity
=======

Probity checks file integrity. It can generate sha1 hashes of files and
arbitrarily nested folders. Probity's output is human-readable and composable:
the hash of a folder is generated using the hashes of its files and subfolders.

Installation
------------
::

    python setup.py install

Usage
-----
To print hashes of individual files and folders::

    probity [files, folders, ...]

To print a full report of hashes for the contents of a folder::

    probity -v [folder]
