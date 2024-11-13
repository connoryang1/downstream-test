import typing

from ._stretched_lookup_ingest_times import stretched_lookup_ingest_times


def stretched_lookup_ingest_times_eager(S: int, T: int) -> typing.List[int]:
    """Ingest time lookup algorithm for stretched curation.

    Parameters
    ----------
    S : int
        Buffer size. Must be a power of two.
    T : int
        Current logical time.

    Returns
    -------
    typing.List[int]
        Ingest time of stored item, if any, at buffer sites in index order.
    """
    if T < S:
        raise ValueError("T < S not supported for eager lookup")
    return list(stretched_lookup_ingest_times(S, T))
