from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


class DownloadFailed(Exception):
    pass


class MediaTooLarge(Exception):
    pass


class UnsupportedMedia(DownloadFailed):
    pass


@contextmanager
def as_download_failed() -> Iterator[None]:
    try:
        yield
    except (DownloadFailed, MediaTooLarge):
        raise
    except Exception as exc:
        raise DownloadFailed(str(exc)) from exc
