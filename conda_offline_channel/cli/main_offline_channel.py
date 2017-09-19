from __future__ import absolute_import, division, print_function

import logging
import os
import sys

from conda_build.conda_interface import ArgumentParser
from ..offline_channel import build_offline_channel


logging.basicConfig(level=logging.INFO)


def parse_args(args):
    p = ArgumentParser(
        description=(
            'Create an offline channel which contains all package'
            'dependencies.'
        ),
    )

    p.add_argument(
        'packages',
        help='Package included in the channel.',
        nargs='*',
        default=[],
    )
    p.add_argument(
        '-r', '--root_dir',
        help='Directory that become an offline channel.',
        default=os.path.join(os.getcwd(), 'channel'),
    )

    p.add_argument(
        '-p', '--platform',
        help='A target platform',
        default=None,
    )

    p.add_argument(
        '-c', '--channel',
        nargs='*',
        default=[],
    )

    p.add_argument(
        '--override-channel',
        action='store_true',
        default=False,
    )

    p.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Don\'t show progress.',
    )

    args = p.parse_args(args)
    return p, args


def execute(args):
    _, args = parse_args(args)
    build_offline_channel(
        args.root_dir,
        args.packages,
        args.platform,
        args.channel,
        not args.override_channel,
        quiet=args.quiet,
    )


def main():
    return execute(sys.argv[1:])
