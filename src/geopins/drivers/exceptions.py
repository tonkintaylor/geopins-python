from typing import Literal, Never, assert_never

from geopins.filetypes import get_filetype_display_name


def raise_driver_not_supported(
    filetype: str, *, cls: type[object], mode: Literal["read", "write"]
) -> Never:
    """Raise a NotImplementedError indicating that the driver is not supported.

    Args:
        filetype: The filetype that is not supported.
        cls: The class for which the driver is not supported.
        mode: Either "read" or "write", indicating whether the driver is not supported
              for reading or writing.

    Different error messages are raised depending on whether the filetype is supported
    for any other Python datatypes in pins or geopins. The messages mimic those used
    in pins for consistency.
    """
    try:
        name = get_filetype_display_name(filetype)
    except NotImplementedError:
        if mode == "read":
            # Matches pins error message in pins.drivers.load_data
            msg = f"No driver for type {type}"
            raise NotImplementedError(msg) from None
        elif mode == "write":
            # Matches pins error message in pins.drivers.save_data
            msg = f"Cannot save type: {filetype}"
            raise NotImplementedError(msg) from None
        else:
            assert_never(mode)
    else:
        if mode == "read":
            # Nothing to match with!
            msg = (
                f"Reading from '{filetype}' format is not supported for {cls.__name__}."
            )
            raise NotImplementedError(msg)
        elif mode == "write":
            # Matches pins error messages in pins._adaptors.Adaptor.write_csv etc.
            msg = f"Writing to {name} is not supported for {cls.__name__}."
            raise NotImplementedError(msg)
        else:
            assert_never(mode)
