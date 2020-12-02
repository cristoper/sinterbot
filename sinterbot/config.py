import os
import re
import logging
from typing import List, Tuple
log = logging.getLogger(__name__)

try:
    import pathlib
except ImportError as e:
    log.error("Can't import pathlib. Make sure you have python version >= 3.4.")
    raise e

class ParseError(Exception):
    """Used for exceptions raised during parsing"""
    def __init__(self, lineno: int):
        self.line = lineno

class Santa:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return "%s %s <%s>" % (self.__class__, self.name, self.email)

Blacklist_T = List[Tuple[Santa, Santa]]
class Blacklist:
    def __init__(self):
        self._bl: Blacklist_T = []

    def __repr__(self):
        s = "%s: {" % self.__class__
        for i, pair in enumerate(self._bl):
            if i > 0:
                s += ", "
            s += "(" + ", ".join(pair) + ")"
        s += "}"
        return s

    def add_names(self, names: Tuple[str, str]):
        self._bl.append(names)

    def get_bl(self) -> Blacklist_T:
        return self._bl

class ConfFile:

    def __init__(self, path: str):
        self.path = pathlib.Path(path).expanduser()

        # Set defaults
        self.m = 2
        self.santas = []
        self.bl = Blacklist()
        self.smtpport = 587
        self.smtppass = os.environ.get("sinter_smtp_pass")
        self.__parse()

    def __parse(self):

        CommentPat = re.compile(r'^\s*#.*')
        LinePat = re.compile(r'^\s*(.+):\s*(.+)\s*')

        with self.path.open() as f:
            for lineno, line in enumerate(f):
                lineno += 1 # start lines at 1
                if line == "\n": continue
                if CommentPat.match(line): continue
                m = LinePat.match(line)

                # Error checking
                # we raise exceptions on errors to make sure program does not
                # continue with unexpected secret santa list
                if m is None:
                    log.error("Could not parse line number: %d" % lineno)
                    raise ParseError(lineno)
                g = m.groups()
                if len(g) != 2:
                    log.error("Error parsing line number: %d" % lineno)
                    raise ParseError(lineno)
                if not len(g[1]):
                    log.error("Missing value on line: %d" % lineno)
                    raise ParseError(lineno)
                
                # Get the value for each type of line
                prefix, val = g[0].casefold(), g[1]
                if prefix == "smtpserver":
                    self.smtpserver = val
                elif prefix == "smtpport":
                    self.smtpport = val
                elif prefix == "smtpuser":
                    self.smtpuser = val
                elif prefix == "smtppass":
                    self.smtppass = val
                elif prefix == "m":
                    self.m = val
                elif prefix == "!":
                    # black lists are given as comma separated pairs with
                    # optional space after comma
                    # "email1@domain.tld,email2@domain.tld"
                    first, second = val.split(',', 2)
                    second = second.strip()
                    self.bl.add_names((first, second))
                else:
                    # no pre-defined prefix, assume this is a santa name
                    self.santas.append(Santa(g[0], val))

