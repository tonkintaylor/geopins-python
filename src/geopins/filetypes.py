from __future__ import annotations


def get_filetype_display_name(filetype: str) -> str:
    """Get a display-friendly name for a filetype.

    Args:
        filetype: The filetype to get the display-friendly name for.

    Returns:
        A display-friendly name for the filetype.

    Raises:
        NotImplementedError: If the filetype is not recognized.
    """
    mapping = {
        "csv": "CSV",
        "arrow": "Apache Arrow",
        "feather": "Feather",
        "table": "CSV",
        "joblib": "Joblib",
        "json": "JSON",
        "parquet": "Parquet",
    }
    try:
        return mapping[filetype]
    except KeyError:
        msg = f"Filetype '{filetype}' is not recognized."
        raise NotImplementedError(msg) from None
