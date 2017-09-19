from conda_build.conda_interface import (ArgumentParser, IndexRecord, Resolve,
                                         context, get_index, specs_from_args,
                                         CondaSession,
                                         subdir, conda_43, conda_44)
from conda.exceptions import CondaError, DryRunExit, MD5MismatchError
from conda.base.constants import PLATFORM_DIRECTORIES


if conda_44:
    from conda.cli.conda_argparse import (add_parser_channels,
                                          add_parser_quiet,
                                          add_parser_show_channel_urls,
                                          add_parser_yes)
    from conda.cli.common import confirm
    from conda.common.io import ProgressBar
    from conda.gateways.connection.download import download as gateway_download
else:
    import hashlib
    from conda.cli.common import (add_parser_channels,
                                  add_parser_quiet,
                                  add_parser_show_channel_urls,
                                  add_parser_yes)
    from conda.cli.common import confirm as _confirm
    from conda.console import ProgressBar as _ProgressBar

    def confirm(*args, **kwargs):
        from argparse import Namespace
        return _confirm(Namespace(yes=False, dry_run=False), *args, **kwargs)


    class ProgressBar(object):
        def __init__(self, description, enabled=True, json=False):
            from conda.console import Bar, ETA
            self.pbar = _ProgressBar(
                maxval=1,
                widgets=[description, Bar(), ' ', ETA()],
            ).start()
            self.json = json

        def update_to(self, fraction):
            if fraction == 1:
                self.pbar.finish()
            else:
                self.pbar.update(fraction)

        def finish(self):
            self.pbar.finish()

        def close(self):
            if self.enabled:
                self.finish()
            self.enabled = False


    # Simplified version
    def gateway_download(url, target_full_path, md5sum,
                         progress_update_callback=None):
        timeout = (context.remote_connect_timeout_secs,
                   context.remote_read_timeout_secs)
        session = CondaSession()
        resp = session.get(url, stream=True,
                           proxies=session.proxies, timeout=timeout)
        resp.raise_for_status()

        content_length = int(resp.headers.get('Content-Length', 0))
        digest_builder = hashlib.new('md5')
        with open(target_full_path, 'wb') as fh:
            streamed_bytes = 0
            for chunk in resp.iter_content(2 ** 14):
                # chunk could be the decompressed form of the real data
                # but we want the exact number of bytes read till now
                streamed_bytes = resp.raw.tell()
                try:
                    fh.write(chunk)
                except IOError as e:
                    message = ("Failed to write to %(target_path)s\n  "
                                "errno: %(errno)d")
                    # TODO: make this CondaIOError
                    raise CondaError(message,
                                        target_path=target_full_path,
                                        errno=e.errno)

                digest_builder.update(chunk)

                if (content_length and
                        0 <= streamed_bytes <= content_length):
                    if progress_update_callback:
                        progress_update_callback(
                            streamed_bytes / content_length
                        )

        if content_length and streamed_bytes != content_length:
            # TODO: needs to be a more-specific error type
            message = dals("""
            Downloaded bytes did not match Content-Length
            url: %(url)s
            target_path: %(target_path)s
            Content-Length: %(content_length)d
            downloaded bytes: %(downloaded_bytes)d
            """)
            raise CondaError(message, url=url,
                                target_path=target_full_path,
                                content_length=content_length,
                                downloaded_bytes=streamed_bytes)

        actual_md5sum = digest_builder.hexdigest()
        if md5sum and actual_md5sum != md5sum:
            raise MD5MismatchError(
                url, target_full_path, md5sum, actual_md5sum
            )
