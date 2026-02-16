import time
from types import SimpleNamespace

import pytest

from app.load import get_datasets


@pytest.mark.slow
def test_s3_dataset_speed():
    """
    Open a dataset from S3 and measure timings.

    This is not a strict pass/fail test but a performance check you can
    compare across runs when you modify the code.
    """
    # pick one variable/level/dataset/region_set you know exists
    params = SimpleNamespace(
        variable="tas_None",
        dataset="ERA5",
        region_set="NUTS-1",
        region_name="NL4",
    )

    # --- Measure open time ---
    t0 = time.perf_counter()
    ds = get_datasets(params)[0]
    t1 = time.perf_counter()
    open_time = t1 - t0

    # --- Measure small read time ---
    da = ds[params.variable]

    t2 = time.perf_counter()
    da.isel(region=0).load()
    t3 = time.perf_counter()
    read_time = t3 - t2

    print(
        f"\n[PERF] open_zarr: {open_time:.3f} s\n"
        f"[PERF] small read: {read_time:.3f} s\n"
    )

    # Keep assert minimal so test always passes unless something is really broken
    assert open_time < 30, f"Open took too long: {open_time:.1f}s"
    assert read_time < 60, f"Read took too long: {read_time:.1f}s"
