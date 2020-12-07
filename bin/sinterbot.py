#!/usr/bin/env python3
import argparse
import logging
import sys
import sinterbot.sinterconf as config

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # derange command
    derangeparser = subparsers.add_parser('derange', help='Read .config file to create a .deranged file containing a valid secret santa assignment.')
    derangeparser.add_argument('path', help='Path to .deranged file')
    derangeparser.add_argument('-f', '--force', help='Derange the config file even if it already contains assignment info.', action='store_true')

    # check command
    viewparser = subparsers.add_parser('check', help='Check that the config file contains a valid derangement')
    viewparser.add_argument('path', help='Path to .deranged file')

    # send command
    sendparser = subparsers.add_parser('send', help='Send every santa an email with the name of their assigned recipient.')

    # view command
    viewparser = subparsers.add_parser('view', help='Show the list of secret santa assignments.')
    viewparser.add_argument('path', help='Path to .deranged file')
    viewparser.add_argument('-u', '--user', dest='email', help='Show only the recipient assigned to the given email address(es).', action='append')


    return parser.parse_args()

def parse_config(path: str) -> config.SinterConf:
    """
    Parse the config file at path. On failure log error and quit.
    """
    try:
        c = config.SinterConf.parse_and_validate(path)
    except FileNotFoundError:
        logging.error("Could not find file at path: %s" % path)
        sys.exit(1)
    except config.ValidateError as e:
        logging.error(e)
        sys.exit(1)
    except config.ParseError as e:
        logging.error("Parse error on line %d" % e.line)
        sys.exit(1)
    return c

def derange(args: argparse.Namespace):
    path = args.path
    c = parse_config(path)
    if c.derangement:
        if not args.force:
            print("Input config (%s) already deranged. Pass the --force option if you'd like to modify it anyway." % path)
            return
        else:
            c.derange()
    c.save_derangement()
    print("Derangement info successfully added to config file.\nUse `sinterbot send %s -c smtp.conf` to send emails!" % path)

def check(args:argparse.Namespace):
    path = args.path
    c = parse_config(path)
    if c.derangement:
        print("Valid derangement found.")
    else:
        print("Config file does not contain derangement. Try running `sinterbot derange %s" % path)
    return

def view(args: argparse.Namespace):
    path = args.path
    c = parse_config(path)
    if not c.derangement:
        print("No derangement found in config file. First run `sinterbot derange %s`" % path)
        return
    if args.email:
        emails = args.email
    else:
        emails = c.santas.emails()
    secrets = c.get_assignments()
    santas = secrets.items()
    # Find longest santa
    max_len = 0
    for santa, recip in santas:
        l = len(santa.name) + len(santa.email)
        if l > max_len: max_len = l
    print("{:^{max_len}}  ->   {:^{max_len}}".format("Santa", "Recipient", max_len=max_len+3))
    for santa, recip in santas:
        if santa.email not in emails: continue
        santaf = "{} <{}>".format(santa.name, santa.email)
        recipf = "{} <{}>".format(recip.name, recip.email)
        print("{:<{max_len}}  ->   {:<{max_len}}".format(santaf, recipf, max_len=max_len+3))
    return
    

def main():
    args = parse_args()

    # Use a little introspection to dispatch subcommands directly to functions
    method = getattr(sys.modules[__name__], args.subcommand)
    method(args)

if __name__ == '__main__':
    main()
