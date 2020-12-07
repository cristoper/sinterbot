from sinterbot import config
import ast
import pathlib
import shutil
import re
import random
import sinterbot.algorithms as algo
from typing import List, Tuple, Optional, Dict
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

Blacklist_T = List[Tuple[str, str]]
class Blacklist:
    def __init__(self):
        self.list: Blacklist_T = []
        self._iterindex = 0

    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.list[self._iterindex]
        except IndexError:
            raise StopIteration
        self._iterindex += 1
        return result

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

class Santa:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return "%s %s <%s>" % (self.__class__, self.name, self.email)

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)

class SantaList:
    def __init__(self, santas: List[Santa] = None):
        if santas is None: santas = []
        self.santas = santas

    def __len__(self):
        return len(self.santas)

    def __contains__(self, email):
        return email in self.emails()
    
    def __getitem__(self, key):
        #TODO allow getting by email address str?
        return self.santas[key]

    def emails(self):
        """Return list of all santa emails"""
        emails = []
        for santa in self.santas:
            emails.append(santa.email)
        return emails

    def add(self, santa):
        self.santas.append(santa)

class SinterConf:
    """
    Should use the parse_and_validate() factory method instead of initializing directly
    """
    def __init__(self, path: str):
        self.path = path

        # Set defaults
        self.derangement: Optional[algo.Permutation] = None
        self.mincycle = 2 # minimum cycle length constraint
        self.santas = SantaList()
        self.bl = Blacklist()

    @staticmethod
    def parse_and_validate(path: str):
        """Factory which parses and validates the config file at path"""
        c = SinterConf(path)
        c.parse()
        c.validate()
        return c

    def bl_to_numeric(self) -> algo.Blacklist:
        """
        Returns blacklist (list of tuple of email addresses) as a
        algorithms.Blacklist (list of tuple of integers)
        """
        emails = self.santas.emails()
        numeric = []
        for pair in self.bl.list:
            numeric.append((emails.index(pair[0]), emails.index(pair[1])))
        return numeric

    def derange(self) -> Optional[algo.Permutation]:
        """
        Creates a derangment of santas and stores it in the derangement
        instance variable. You must call parse() and should call validate() (or
        parse_and_validate()) before creating the derangement.
        """
        n = len(self.santas)
        if n < 2: return None
        bl = self.bl_to_numeric()
        self.derangement = algo.constrained(n, self.mincycle, bl)
        return self.derangement

    def save_derangement(self):
        """
        Save the derangement to the config file, first calling `derange()` if
        needed.
        """
        if self.derangement is None:
            self.derange()

        # We first copy all the non 'derangement:' lines from existing config
        # file to a tmp file with a .deranged extension, and then write the new
        # derangement to the end of the file, and finally replace the old file
        # with the new one.
        spath = pathlib.Path(self.path).expanduser()
        dpath = pathlib.Path(self.path + ".deranged").expanduser()
        deranged_re = re.compile(r'^\s*derangement:')
        with spath.open(mode='r') as src:
            with dpath.open(mode='w') as dest:
                for line in src:
                    if deranged_re.match(line) is None:
                        dest.write(line)
                dest.write("derangement:%s" % repr(self.derangement))
        shutil.move(dpath, spath)

    def get_assignments(self) -> Dict[Santa, Santa]:
        """
        Returns a dict of secret santa assignments based on the value of
        self.derangement. If self.derangement is empty, get_assignments will
        first call derange() to populate it.
        """
        if self.derangement is None:
            self.derange()
        assert self.derangement is not None # make mypy happy
        assignment = {}
        for santa, recipient in enumerate(self.derangement):
            assignment[self.santas[santa]] = self.santas[recipient]
        return assignment

    def validate(self):
        """
        Raises an exception of type ValidateError (with informative __str__) if
        this ConfFile fails its consistency checks.
        """
        n = len(self.santas)
        if n < 2:
            raise ValidateError("Config file must list at least two santas")

        if self.mincycle < 2:
            log.error("mincycle set to %d. Using default value of 2." % self.mincycle)
            self.mincycle = 2
            #raise ValidateError("m constraint must be at least 2")

        if self.mincycle > n:
            raise ValidateError("mincycle (%d) is greater than number of santas (%d)." % (self.mincycle, n))

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

        # validate derangement against constraints
        if self.derangement:
            if len(self.derangement) != len(self.santas):
                raise ValidateError("Derangement length does not match length of santa list")

            try:
                valid = algo.check_constraints(self.derangement, self.mincycle,
                    self.bl_to_numeric())
            except ValueError:
                # something wrong with derangement values
                raise ValidateError("Derangement fails validation: %s" %
                        repr(self.derangement))
            if not valid:
                raise ValidateError("Derangement fails validation: %s" %
                        repr(self.derangement))

        # TODO: validate constraints allow for at least 1 valid derangement!

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
            if prefix == "mincycle":
                self.mincycle = int(val)
            elif prefix == "!":
                # black lists are given as comma separated pairs with
                # optional space after comma
                # "email1@domain.tld,email2@domain.tld"
                first, second = val.split(',', 2)
                second = second.strip()
                self.bl.add_emails((first, second))
            elif prefix == "derangement":
                self.derangement = ast.literal_eval(val)
                if not isinstance(self.derangement, list):
                    raise ParseError(kv.lineno)
            else:
                # no pre-defined prefix, assume this is a santa name
                self.santas.add(Santa(kv.key, val))
