import logging

import numpy as np
import polars as pl

from ._impl._check_expected_columns import check_expected_columns


def _check_df(df: pl.DataFrame) -> None:
    """Validate input DataFrame for unpack_data_packed.

    Raises a ValueError if any of the required columns are missing from the
    DataFrame.
    """
    check_expected_columns(
        df,
        expected_columns=[
            "data_hex",
            "dstream_algo",
            "dstream_storage_bitoffset",
            "dstream_storage_bitwidth",
            "dstream_T_bitoffset",
            "dstream_T_bitwidth",
            "dstream_S",
        ],
    )


def _enforce_hex_aligned(df: pl.DataFrame, col: str) -> None:
    """Raise NotImplementedError if column is not hex-aligned (i.e., not a
    multiple of 4 bits)."""
    if (
        not df.lazy()
        .filter((pl.col(col) & pl.lit(0b11) != 0))
        .limit(1)
        .collect()
        .is_empty()
    ):
        raise NotImplementedError(f"{col} not hex-aligned")


def _make_empty() -> pl.DataFrame:
    """Create an empty DataFrame with the expected columns for
    unpack_data_packed, handling edge case of empty input."""
    return pl.DataFrame(
        [
            pl.Series(name="dstream_algo", values=[], dtype=pl.String),
            pl.Series(name="dstream_data_id", values=[], dtype=pl.UInt64),
            pl.Series(name="downstream_version", values=[], dtype=pl.String),
            pl.Series(name="dstream_S", values=[], dtype=pl.UInt32),
            pl.Series(name="dstream_T", values=[], dtype=pl.UInt64),
            pl.Series(name="dstream_storage_hex", values=[], dtype=pl.String),
        ],
    )


def unpack_data_packed(
    df: pl.DataFrame, *, relax_dtypes: bool = False
) -> pl.DataFrame:
    """Unpack data with dstream buffer and counter serialized into a single
    hexadecimal data field.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per dstream buffer.

        Required schema:
            - 'data_hex' : pl.String
                - Raw binary data, with serialized dstream buffer and counter.
                - Represented as a hexadecimal string.
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_storage_bitoffset' : pl.UInt64
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt64
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt64
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt64
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.UInt32
                - Capacity of dstream buffer, in number of data items.

        Optional schema:
            - 'downstream_version' : pl.Categorical
                - Version of downstream library used to curate data items.

    relax_dtypes : bool = False
        If set to True, calls `shrink_dtype()` on all columns before the
        final DataFrame is returned, thereby saving memory.

    Returns
    -------
    pl.DataFrame
        Processed DataFrame with unpacked and decoded data fields, one row per
        dstream buffer

        Output schema:
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_data_id' : pl.UInt64
                - Row index identifier for dstream buffer.
            - 'dstream_S' : pl.UInt32
                - Capacity of dstream buffer, in number of data items.
            - 'dstream_T' : pl.UInt64
                - Logical time elapsed (number of elapsed data items in stream).
            - 'dstream_storage_hex' : pl.String
                - Raw dstream buffer binary data, containing packed data items.
                - Represented as a hexadecimal string.

        User-defined columns and 'downstream_version' will be forwarded from
        the input DataFrame.

    Raises
    ------
    NotImplementedError
        If any of the bit offset or bit width columns are not hex-aligned
        (i.e., not multiples of 4 bits).
    ValueError
        If any of the required columns are missing from the input DataFrame.


    See Also
    --------
    downstream.dataframe.explode_lookup_unpacked :
        Explodes unpacked buffers into individual constituent data items.
    """
    logging.info("begin explode_lookup_unpacked")
    logging.info(" - prepping data...")

    _check_df(df)
    if df.lazy().limit(1).collect().is_empty():
        return _make_empty()

    df = df.cast({"data_hex": pl.String, "dstream_algo": pl.Categorical})

    logging.info(" - calculating offsets...")
    for col in (
        "dstream_storage_bitoffset",
        "dstream_storage_bitwidth",
        "dstream_T_bitoffset",
        "dstream_T_bitwidth",
    ):
        _enforce_hex_aligned(df, col)
        df = df.with_columns(
            **{col.replace("_bit", "_hex"): np.right_shift(pl.col(col), 2)},
        )

    if "dstream_data_id" not in df.lazy().collect_schema().names():
        df = df.with_row_index("dstream_data_id")

    logging.info(" - extracting T and storage_hex from data_hex...")

    df = (
        df.lazy()
        .with_columns(
            dstream_storage_hex=pl.col("data_hex").str.slice(
                pl.col("dstream_storage_hexoffset"),
                length=pl.col("dstream_storage_hexwidth"),
            ),
            dstream_T=pl.col("data_hex")
            .str.slice(
                pl.col("dstream_T_hexoffset"),
                length=pl.col("dstream_T_hexwidth"),
            )
            .str.to_integer(base=16)
            .cast(pl.Uint64),
        )
        .drop(
            [
                "data_hex",
                "dstream_storage_hexoffset",
                "dstream_storage_hexwidth",
                "dstream_T_hexoffset",
                "dstream_T_hexwidth",
                "dstream_storage_bitoffset",
                "dstream_storage_bitwidth",
                "dstream_T_bitoffset",
                "dstream_T_bitwidth",
            ],
        )
        .collect()
    )

    if relax_dtypes:
        return df.select(pl.all().shrink_dtype())

    logging.info("unpack_data_packed complete")
    return df
