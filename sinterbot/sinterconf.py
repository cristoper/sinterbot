import os
import sinterbot.config as config
import random
import sinterbot.algorithms as algo
from typing import List, Tuple, Optional
import logging
# TODO enable/disable logging
log = logging.getLogger(__name__)

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

class SinterConf:
    def __init__(self, path: str):
        self.path = path

        # Set defaults
        self.derangement: Optional[algo.Permutation] = None
        self.m = 2
        self.santas = SantaList()
        self.bl = Blacklist()

    @staticmethod
    def parse_and_validate(path: str):
        """Factory which parses and validates the config file at path"""
        c = SinterConf(path)
        c.parse()
        c.validate()
        return c

    def derange(self) -> Optional[algo.Permutation]:
        """Creates a derangment of santas"""
        emails = self.santas.emails()
        n = len(emails)
        if n < 2: return None
        m = self.m
        if m < 2:
            # if m == 1, we want only a single cycle which is the same as m = n
            m = n
        bl = []
        for pair in self.bl.list:
            bl.append((emails.index(pair[0]), emails.index(pair[1])))
        #TODO: use more efficient algorithm
        valid = algo.generate_all(n, m, bl)
        self.derangement = random.choice(valid)
        return self.derangement

    def validate(self):
        """
        Raises an exception of type ValidateError (with informative __str__) if
        this ConfFile fails its consistency checks.
        """
        if len(self.santas.santas) < 2:
            raise ValidateError("Config file must list at least two santas")

        if self.m < 1:
            raise ValidateError("m constraint must be at least 1")

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
        # TODO: if derangement is populated, check that it meets constraints!


    def parse(self):
        """Parses the file at self.path and populates instance variables.

        Does not validate settings (for that see `validate()`)
        """

        conf = config.Conf(self.path)
        for kv in conf.parse():
            # We raise exceptions on errors to make sure program does not
            # continue with unexpected secret santa list
            if kv.error:
                log.error("Parse error on line %d: %s" % (kv.lineno, kv.error))
                raise ParseError(kv.lineno)

            # Get the value for each type of line
            prefix, val = kv.key.casefold(), kv.value
            if prefix == "smtpserver":
                self.smtpserver = val
            elif prefix == "smtpport":
                self.smtpport = val
            elif prefix == "smtpuser":
                self.smtpuser = val
            elif prefix == "smtppass":
                self.smtppass = val
            elif prefix == "m":
                self.m = int(val)
            elif prefix == "!":
                # black lists are given as comma separated pairs with
                # optional space after comma
                # "email1@domain.tld,email2@domain.tld"
                first, second = val.split(',', 2)
                second = second.strip()
                self.bl.add_emails((first, second))
            else:
                # no pre-defined prefix, assume this is a santa name
                self.santas.add(Santa(kv.key, val))

