#!/usr/bin/env python3
import argparse
import logging
import sys
import sinterbot.sinterconf as config

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    derangeparser = subparsers.add_parser('derange', help='Read .config file to create a .deranged file containing a valid secret santa assignment.')
    derangeparser.add_argument('path', help='Path to .deranged file')
    derangeparser.add_argument('-f', '--force', help='Derange the config file even if it already contains assignment info.', action='store_true')

    sendparser = subparsers.add_parser('send', help='Send every santa an email with the name of their assigned recipient.')

    viewparser = subparsers.add_parser('view', help='Show the list of secret santa assignments.')
    viewparser.add_argument('path', help='Path to .deranged file')
    return parser.parse_args()


def derange(args: argparse.Namespace):
    path = args.path
    try:
        c = config.SinterConf.parse_and_validate(path)
    except FileNotFoundError:
        logging.error("Could not find file at path: %s" % path)
        return
    except config.ValidateError as e:
        logging.error(e)
        return
    except config.ParseError as e:
        logging.error("Parse error on line %d" % e.line)
        return
    if c.derangement:
        if not args.force:
            print("Input config (%s) already deranged. Pass the --force option if you'd like to modify it anyway." % path)
            return
        else:
            c.derange()
    c.save_derangement()
    print("Derangement info successfully added to config file.\nUse `sinterbot send %s -c smtp.conf` to send emails!" % path)

def view(args: argparse.Namespace):
    path = args.path
    c = config.SinterConf.parse_and_validate(path)
    print(c.assignments_str())
    

def main():
    args = parse_args()

    # Use a little introspection to dispatch subcommands directly to functions
    method = getattr(sys.modules[__name__], args.subcommand)
    method(args)

if __name__ == '__main__':
    main()
