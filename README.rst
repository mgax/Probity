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

TODO list
---------

* from a checksum report of a large folder, extract the section for a given
  subfolder (it's a pain to do this manually)

* compare a checksum report to the contents of a given folder
