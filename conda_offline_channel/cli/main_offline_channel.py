from __future__ import absolute_import, division, print_function

import os
import sys

from ..conda_interface import (ArgumentParser, DryRunExit, add_parser_channels,
                               add_parser_quiet, add_parser_show_channel_urls,
                               add_parser_yes)
from ..offline_channel import build_channel


def parse_args(args):
    p = ArgumentParser(
        description=(
            'Create an offline channel which contains all package'
            'dependencies.'
        ),
    )

    p.add_argument(
        'package_specs',
        help='Packages will be included in the offline channel.',
        nargs='+',
        default=[],
    )

    p.add_argument(
        '-r', '--root-dir',
        help='Directory that become an offline channel.',
        default=os.path.join(os.getcwd(), 'channel'),
    )

    p.add_argument(
        '-p', '--platform',
        help='A target platform',
        default=None,
    )

    p.add_argument(
        '-k', '--ignore-builtins',
        help='Ignore dependencies included in "conda" package',
        default=False,
        action='store_true',
    )
    p.add_argument(
        '-i', '--ignores',
        help='Ignore dependencies of given package',
        action='append',
    )

    add_parser_channels(p)
    add_parser_quiet(p)
    add_parser_show_channel_urls(p)
    add_parser_yes(p)

    args = p.parse_args(args)

    return p, args


def execute(args):
    _, args = parse_args(args)
    build_channel(
        args.package_specs,
        args.root_dir,
        channel_urls=args.channel or (),
        prepend=not args.override_channels,
        platform=args.platform,
        quiet=args.quiet,
        confirm_proceed=not args.yes,
        show_channel_urls=args.show_channel_urls,
        ignore_builtins=args.ignore_builtins,
        ignores=args.ignores,
    )


def main():
    try:
        return execute(sys.argv[1:])
    except DryRunExit:
        pass
