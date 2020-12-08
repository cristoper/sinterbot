
import os
import sinterbot.config as config
import logging
# TODO enable/disable logging
log = logging.getLogger(__name__)


class ParseError(Exception):
    """Used for exceptions raised during parsing"""
    def __init__(self, lineno: int):
        self.line = lineno


class SMTPConf:
    def __init__(self, path: str):
        self.path = path
        self.server: str = ""
        self.port = 587
        self.email: str = ""
        self.user: str = ""
        self.password = os.environ.get("sinter_smtp_pass")

    def parse(self):
        """
        Parses the file at self.path and populates instance variables.
        """

        conf = config.Conf(self.path)
        for kv in conf.parse():

            # Error checking
            if kv.error:
                log.error("Parse error on line %d: %s" % (kv.lineno, kv.error))
                raise ParseError(kv.lineno)

            # Get the value for each type of line
            prefix, val = kv.key.casefold(), kv.value
            if prefix == "smtpserver":
                self.server = val
            elif prefix == "smtpport":
                self.port = val
            elif prefix == "smtpemail":
                self.email = val
                if not self.user:
                    # smtpuser defaults to smtpemail
                    self.user = val
            elif prefix == "smtpuser":
                self.user = val
            elif prefix == "smtppass":
                self.password = val
            else:
                log.error("Unrecognized key on line %d, ignoring: %s" % (kv.lineno, kv.key))
