from typing import Union

import numpy as np
import xarray as xr


def ensure_float(
    data: Union[xr.DataArray, xr.Dataset]
) -> Union[xr.DataArray, xr.Dataset]:
    """
    Ensure the DataArray or Dataset contains float values.

    If it's a timedelta64, convert it to float days.
    """
    if isinstance(data, xr.Dataset):
        return data.map(ensure_float)

    if np.issubdtype(data.dtype, np.timedelta64):
        # Convert to float days precisely
        return data / np.timedelta64(1, "D")
    return data.astype(float)
