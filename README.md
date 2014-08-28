bootstrap3-upgrader
===================

Python script for upgrading Bootstrap CSS 2.x to 3.x based on raw
string processing and regular expression matching. This script does
not use a DOM-parsing approach so it can be safely used to process
template files which cannot be processed with a DOM parser.

This initial version parses HTML but also takes template processing
instructions into account. Currently this is limited to template tags
starting with ``{%`` and ending with ``%}``, currently.


See http://getbootstrap.com/migration/ for an overview of what this
tool processes.

Known issues / TO DO
--------------------

- Navbar classes need to be adjusted manually


Alternatives
------------

For DOM-based processing see projects like https://github.com/divshot/bootstrap3_upgrader
