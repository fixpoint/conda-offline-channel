import os
import typing

from conda._vendor import progressbar
from conda_build.config import Config
from conda_build.index import update_index
from conda_build.conda_interface import (Resolve, get_index, specs_from_args,
                                         subdir, CondaSession)

if typing.TYPE_CHECKING:
    from typing import Collection, Iterator  # noqa: F401

    from conda_build.conda_interface import IndexRecord  # noqa: F401


def _resolve_records(packages,      # type: Collection[str]
                     platform,      # type: str
                     channel_urls,  # type: Collection[str]
                     prepend,       # type: bool
                     ):
    # type: (...) -> Iterator[IndexRecord]
    specs = specs_from_args(packages)
    index = get_index(channel_urls=channel_urls,
                      prepend=prepend,
                      platform=platform)
    r = Resolve(index)
    for dist in r.solve(specs):
        yield index[dist]


def _fetch_package(session, label, record, root_dir, chunk_size, quiet):
    # type: (CondaSession, str, IndexRecord, str, int, bool) -> None
    subdir = record.channel.rsplit('/', 1)[-1]
    output = os.path.join(root_dir, subdir)
    os.makedirs(output, exist_ok=True)
    if quiet:
        bar = lambda x: x  # noqa: E731
    else:
        bar = progressbar.ProgressBar(
            maxval=record.size,
            widgets=['%s ' % label, progressbar.Bar()],
        )
    r = session.get(record.url, stream=True)
    r.raise_for_status()
    with open(os.path.join(output, record.fn), 'bw') as fd:
        for chunk in bar(r.iter_content(chunk_size)):
            fd.write(chunk)


def build_offline_channel(root_dir,         # type: str
                          packages,         # type: Collection[str]
                          platform=None,    # type: str
                          channel_urls=(),  # type: Collection[str]
                          prepend=True,     # type: bool
                          chunk_size=1024,  # type: int
                          quiet=False,      # type: bool
                          ):
    # type: (...) -> None
    """Build a conda channel which contains all dependencies of packages for
    offline usage

    Args:
        root_dir: channel root directory
        packages: conda packages
        channel_urls: channel urls used to download packages and dependencies
        prepend: prepend channels specified to the default channels
        chunk_size: chunk size for downloading packages
        quiet: do not show progressbar
    """
    os.makedirs(os.path.join(root_dir, 'noarch'), exist_ok=True)
    os.makedirs(os.path.join(root_dir, subdir), exist_ok=True)

    # resolve records from packages
    records = tuple(_resolve_records(packages, platform, channel_urls,
                                     prepend))
    labels = ['%s %s' % (r.name, r.version) for r in records]
    maxlen = max(map(len, labels))
    # fetch packages into the channel
    session = CondaSession()
    for label, record in zip(labels, records):
        _fetch_package(session=session,
                       label=label.rjust(maxlen),
                       record=record,
                       root_dir=root_dir,
                       chunk_size=chunk_size,
                       quiet=quiet)
    # build index

    kwargs = dict(
        force=False,
        check_md5=False,
        remove=True,
        lock=None,
        could_be_mirror=True,
    )
    config = Config(verbose=not quiet)
    try:
        update_index(
            os.path.join(root_dir, 'noarch'),
            config=config,
            **kwargs
        )
        update_index(
            os.path.join(root_dir, subdir),
            config=config,
            **kwargs
        )
    except TypeError:
        # conda-build 2.x.x did not support 'config'
        # ref: 95eefe623c26f456872fe8761f4d0448dba76b49
        update_index(
            os.path.join(root_dir, 'noarch'),
            verbose=not quiet,
            **kwargs
        )
        update_index(
            os.path.join(root_dir, subdir),
            verbose=not quiet,
            **kwargs
        )
