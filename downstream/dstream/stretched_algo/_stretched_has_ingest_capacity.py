from ._stretched_get_ingest_capacity import stretched_get_ingest_capacity


def stretched_has_ingest_capacity(S: int, T: int) -> bool:
    """Does this algorithm have the capacity to ingest a data item at logical
    time T?

    Parameters
    ----------
    S : int
        The number of buffer sites available.
    T : int
        Current logical time.

    Returns
    -------
    bool

    See Also
    --------
    get_ingest_capacity : How many data item ingestions does this algorithm
    support?
    """
    assert T >= 0
    ingest_capacity = stretched_get_ingest_capacity(S)
    return ingest_capacity is None or T < ingest_capacity


has_ingest_capacity = stretched_has_ingest_capacity  # lazy loader workaround
