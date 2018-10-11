from __future__ import absolute_import, division, print_function

import os

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

from conda_build.index import update_index

from .conda_interface import (PLATFORM_DIRECTORIES, ProgressBar, Resolve,
                              confirm, context, gateway_download, get_index,
                              specs_from_args)

if TYPE_CHECKING:
    from typing import Collection, Callable, Iterator     # noqa: F401
    from .conda_interface import IndexRecord    # noqa: F401


def solve_dependencies(package_specs,    # type: Collection[str]
                       channel_urls=(),  # type: Collection[str]
                       prepend=True,     # type: bool
                       platform=None,    # type: str
                       use_local=False,  # type: bool
                       use_cache=False,  # type: bool
                       ):
    # type: (...) -> Iterator[IndexRecord]
    specs = specs_from_args(package_specs)
    index = get_index(channel_urls=channel_urls,
                      prepend=prepend,
                      platform=platform,
                      use_local=use_local,
                      use_cache=use_cache)
    r = Resolve(index)
    for dist in r.solve(specs, _remove=True):
        yield index[dist]


def download_to_channel(
        record,                        # type: IndexRecord
        channel_dir,                   # type: str
        progress_update_callback=None  # type: Callable[[float], None]
        ):
    # type: (...) -> None
    dst = os.path.join(
        channel_dir,
        getattr(record, 'subdir', context.subdir),
        record.fn,
    )
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    gateway_download(record.url, dst,
                     md5sum=record.md5,
                     progress_update_callback=progress_update_callback)


def update_channel_indices(channel_dir, **kwargs):
    for subdir in PLATFORM_DIRECTORIES:
        path = os.path.join(channel_dir, subdir)
        if not os.path.exists(path):
            continue
        update_index(path, **kwargs)


def build_channel(package_specs,    # type: Collection[str]
                  channel_dir,      # type: str
                  channel_urls=(),  # type: Collection[str]
                  prepend=True,     # type: bool
                  platform=None,    # type: str
                  use_local=False,  # type: bool
                  use_cache=False,  # type: bool
                  quiet=False,      # type: bool
                  confirm_proceed=True,     # type: bool
                  show_channel_urls=False,  # type: bool
                  ignore_builtins=False,    # type: bool
                  ignores=(),       # type: Collection[str]
                  ):
    # type: (...) -> None
    packages = set(solve_dependencies(
        package_specs,
        channel_urls=channel_urls,
        prepend=prepend,
        platform=platform,
        use_local=use_local,
        use_cache=use_cache,
    ))

    if ignore_builtins:
        # Remove builtin packages
        packages -= set(solve_dependencies(
            ['conda'],
            channel_urls=channel_urls,
            prepend=prepend,
            platform=platform,
            use_local=use_local,
            use_cache=use_cache,
        ))
    if ignores:
        # Remove given packages
        packages -= set(solve_dependencies(
            list(ignores),
            channel_urls=channel_urls,
            prepend=prepend,
            platform=platform,
            use_local=use_local,
            use_cache=use_cache,
        ))

    if not packages:
        print('No dependencies are detected.')
        return

    if not quiet:
        maxsize_name = max((len(p.name) for p in packages))
        maxsize_version = max((len(p.version) for p in packages))
        print('The following packages will be DOWNLOADED:')
        print('')
        for p in packages:
            msg = '\t%s %s %s' % (
                (p.name + ':').ljust(maxsize_name + 1),
                p.version.ljust(maxsize_version),
                p.channel if show_channel_urls else p.schannel,
            )
            try:
                msg += ' ' + ' '.join(p.features)
            except AttributeError:
                pass
            print(msg)
        print('')

    if confirm_proceed and confirm() == 'no':
        return

    descriptions = [os.path.basename(p.fn) for p in packages]
    maxsize_description = max((len(d) for d in descriptions))
    for d, p in zip(descriptions, packages):
        pbar = ProgressBar(
            d.ljust(maxsize_description + 1),
            enabled=not quiet,
        )
        download_to_channel(p, channel_dir, pbar.update_to)

    update_channel_indices(channel_dir, verbose=not quiet)
