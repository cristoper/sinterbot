"""
This module implements a parser for a basic untyped (everything is a string)
key-value configuration file. Example:
---

    # Blank lines and lines whose first non-whitespace character is a '#' are
    # ignored.  all other lines are colon-separated 'key: value' pairs (white
    # space around keys and values is ignored):
    key1: value1
    key2:value2
    key3: value3
"""
import re
import logging
# TODO enable/disable logging
log = logging.getLogger(__name__)

try:
    import pathlib
except ImportError as e:
    log.error("Can't import pathlib. Make sure you have python version >= 3.4")
    raise e

class KeyValue:
    def __init__(self, lineno: int, key: str = "", value: str = "", error: str = None):
        self.key = key
        self.value = value
        self.lineno = lineno
        self.error = error

class Conf:
    def __init__(self, path: str):
        self.path = pathlib.Path(path).expanduser()

    def parse(self):
        """Parses the file at self.path and yields all found 'key: value' pairs
        as a stream of KeyValue objects
        """

        CommentPat = re.compile(r'^\s*#.*')
        LinePat = re.compile(r'^\s*(.+):\s*(.+)?\s*')

        with self.path.open() as f:
            for lineno, line in enumerate(f):
                lineno += 1 # start lines at 1
                if line == "\n": continue
                if CommentPat.match(line): continue
                m = LinePat.match(line)

                # Error checking
                # If an error is found on a line, the returned KeyValue object
                # will have its error field populated is returned.
                if m is None:
                    yield KeyValue(lineno, error="Could not parse line number: %d" % lineno)
                    continue
                g = m.groups()
                if len(g) != 2:
                    yield KeyValue(lineno, error="No value found")
                    continue
                if g[1] == None:
                    g = (g[0], "")
                
                yield KeyValue(lineno, g[0], g[1], error=None)
