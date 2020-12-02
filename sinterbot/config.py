import os
import re
import logging
from typing import List, Tuple
# TODO enable/disable logging
log = logging.getLogger(__name__)

try:
    import pathlib
except ImportError as e:
    log.error("Can't import pathlib. Make sure you have python version >= 3.4")
    raise e

class ParseError(Exception):
    """Used for exceptions raised during parsing"""
    def __init__(self, lineno: int):
        self.line = lineno

class ValidateError(Exception):
    """Used for exceptions during validation"""
    def __init__(self, msg: str = ""):
        self.msg = msg

    def __str__(self):
        return self.msg

class Santa:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return "%s %s <%s>" % (self.__class__, self.name, self.email)

class SantaList:
    def __init__(self, santas: List[Santa] = None):
        if santas is None: santas = []
        self.santas = santas

    def emails(self):
        """Return list of all santa emails"""
        emails = []
        for santa in self.santas:
            emails.append(santa.email)
        return emails

    def add(self, santa):
        self.santas.append(santa)

Blacklist_T = List[Tuple[str, str]]
class Blacklist:
    def __init__(self):
        self.list: Blacklist_T = []

    def __repr__(self):
        s = "%s: {" % self.__class__
        for i, pair in enumerate(self.list):
            if i > 0:
                s += ", "
            s += "(" + ", ".join(pair) + ")"
        s += "}"
        return s

    def add_emails(self, emails: Tuple[str, str]):
        self.list.append(emails)

class ConfFile:
    def __init__(self, path: str):
        self.path = pathlib.Path(path).expanduser()

        # Set defaults
        self.m = 2
        self.santas = SantaList()
        self.bl = Blacklist()
        self.smtpport = 587
        self.smtppass = os.environ.get("sinter_smtp_pass")

    @staticmethod
    def parse_and_validate(path: str):
        """Factory which parses and validates the config file at path"""
        c = ConfFile(path)
        c.parse()
        c.validate()
        return c

    def validate(self):
        """
        Raises an exception of type ValidateError (with informative __str__) if
        this ConfFile fails its consistency checks.
        """
        if len(self.santas.santas) < 2:
            raise ValidateError("Config file must list at least two santas")

        # make sure all santas have unique email addresses
        emails = self.santas.emails()
        unique_emails = set(emails)
        if len(emails) != len(unique_emails):
            raise ValidateError("All email addresses must be unique")

        # make sure the black list contains only email addresses listed as santas
        for pair in self.bl.list:
            for email in pair:
                if email.casefold() not in self.santas.emails():
                    raise ValidateError("Black list contains email not listed in santas: %s" % email)

        # TODO: validate constraints allow for at least 1 valid derangement!


    def parse(self):
        """Parses the file at self.path and populates instance variables.

        Does not validate settings (for that see `validate()`)
        """

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
                    self.bl.add_emails((first, second))
                else:
                    # no pre-defined prefix, assume this is a santa name
                    self.santas.add(Santa(g[0], val))

