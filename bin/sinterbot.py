#!/usr/bin/env python3
import argparse
import sys
import sinterbot.sinterconf as config

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    derangeparser = subparsers.add_parser('derange', help='Read .config file to create a .deranged file containing a valid secret santa assignment.')
    derangeparser.add_argument('path', help='Path to .deranged file')

    sendparser = subparsers.add_parser('send', help='Send every santa an email with the name of their assigned recipient.')

    viewparser = subparsers.add_parser('view', help='Show the list of secret santa assignments.')
    viewparser.add_argument('path', help='Path to .deranged file')
    return parser.parse_args()


def derange(args: argparse.Namespace):
    path = args.path
    c = config.SinterConf.parse_and_validate(path)
    c.save_derangement()

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
