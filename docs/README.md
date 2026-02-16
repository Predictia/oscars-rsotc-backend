# Regional State of the Climate Backend API

This is the backend API for the Regional State of the Climate Dashboard. It provides a REST API for accessing climate data and performing various climate analysis tasks.

![Backend Architecture Flowchart](docs/_static/flowchart.png)

## Development

This project uses [pixi](https://pixi.sh) for dependency management and environment handling.

### Prerequisites

You need to have `pixi` installed on your system. Follow the instructions on the [official website](https://pixi.sh/latest/#installation).

### Environment Setup

The project defines two main environments:

- `dev` (default): Includes all dependencies needed for development and testing.
- `docs`: Includes dependencies for building documentation.

To install the dependencies and set up the environments, run:

```bash
pixi install
```

### Common Tasks

You can run various tasks using `pixi run`.

| Task | Description | Command |
| :--- | :--- | :--- |
| `dev` | Run the application | `pixi run dev` |
| `qa` | Run pre-commit hooks (linting, formatting) | `pixi run qa` |
| `unit-tests` | Run pytest with coverage | `pixi run unit-tests` |
| `type-check` | Run mypy type checking | `pixi run type-check` |
| `docs-build` | Build HTML documentation | `pixi run -e docs docs-build` |
| `docker-build` | Build the Docker image | `pixi run docker-build` |
| `docker-run` | Run the Docker container | `pixi run docker-run` |

### Configuration

Before running the project, copy the sample environment file and fill in your credentials:

```bash
cp .env-sample .env
```

## Data Loading

The backend uses a flexible data loading mechanism defined in `app/load.py`. It manages datasets stored in [Zarr](https://zarr.readthedocs.io/en/stable/) format.

### Configuration

Data source is configured via environment variables (see `.env-sample`):

- `S3_BUCKET_NAME`: The name of the S3 bucket containing the data.
- `S3_ENDPOINT_URL`: The URL of the S3 service.
- `S3_ACCESS_KEY`: S3 access key.
- `S3_SECRET_KEY`: S3 secret key.

### Loading Logic

1. **Dataset Mapping**: On startup or first request, the backend scans the S3 bucket for `.zarr` files and builds a mapping based on the filename structure: `{variable}_{level}_{dataset}_{region_set}.zarr`.
1. **Local Fallback**: When a dataset is requested, the backend first attempts to find it in the local directory specified by `LOCAL_DATA_DIR` (default: `/data`). This is useful for local development or when data is pre-downloaded.
1. **S3 Fetching**: If the local file is not found, it streams the data directly from S3 using `fsspec` and `xarray`.

## API Endpoints

All endpoints are available under the `/api` prefix.

### `GET /api/time_series`

Calculates a time series for a specific variable and region.

**Parameters:**

- `dataset` (string, required): Dataset name (e.g., 'ERA5').
- `region_set` (string, required): Region set ID.
- `region_name` (string, required): Specific region name.
- `variable` (string, required): Variable name (e.g., 'tas_None').
- `resample_freq` (string, optional, default: 'M'): Resampling frequency.
- `resample_func` (string, optional, default: 'mean'): Resampling function.
- `period` (string, optional, default: 'all'): Time period.
- `season_filter` (string, optional, default: '01-12'): Seasonal filter.
- `season_filter_func` (string, optional, default: 'mean'): Seasonal filter function.
- `anomaly` (boolean, optional, default: false): Whether to return anomalies.
- `reference_period` (string, optional): Reference period for anomalies.

**Response:**

- `date`: List of dates.
- `value`: Dictionary with variable names as keys and lists of values.

### `GET /api/climatology_map`

Generates data for a climatology map across all regions in a set.

**Parameters:**

- Same as `time_series`, but `resample_freq` defaults to `None`.

**Response:**

- `region`: List of region IDs.
- `data`: List of values corresponding to each region.

### `GET /api/annual_cycle`

Provides the statistical annual cycle (percentiles, min/max).

**Parameters:**

- `dataset`, `region_set`, `region_name`, `variable` (required).
- `resample_freq` (optional, default: 'M').
- `period` (optional, default: '2024-2024').
- `reference_period` (optional, default: '1940-2023').

**Response:**

- Includes `date`, `value`, `percentile90`, `median`, `percentile10`, `min`, `max`, `higher_than_max`, `lower_than_min`.

### `GET /api/extreme_values`

Finds extreme values for a given period.

**Parameters:**

- `dataset`, `region_set`, `region_name`, `variable` (required).
- `period` (optional, default: '2024-2024').
- `season_filter` (optional, default: '01-12').

**Response:**

- `date_min`, `value_min`, `date_max`, `value_max`.

### `GET /api/histograms`

Compares frequency distributions between two periods.

**Parameters:**

- `dataset`, `region_set`, `region_name`, `variable` (required).
- `period` (optional, default: 'all').
- `reference_period` (optional, default: '1950-1990').
- `season_filter` (optional, default: '01-12').

**Response:**

- `bins`, `value_period`, `value_reference`, `max_value_period`, `max_value_reference`, `max_date_period`, `max_date_reference`.

### `POST /api/summary_stats`

Generates a structured summary of climate conditions for multiple variables.

**Parameters (JSON Body):**

- `dataset` (string, optional, default: 'ERA5').
- `region_set` (string, optional, default: 'NUTS-0').
- `region_name` (string, required).
- `period` (string, optional, default: '2024-2024'): The target year or range.
- `season_filter` (string, optional, default: '01-12'): Seasonal filter (e.g., '03-03' for March).

**Response:**

- `items`: A list of objects, each containing:
  - `variable`: Short name of the variable.
  - `long_name`: Descriptive name.
  - `unit`: Unit of measurement.
  - `value`: Calculated value for the target period/season.
  - `anomalies`: Dictionary of anomalies against standard reference periods (1961-1990, 1971-2000, 1981-2010, 1991-2020).
  - `ref_means`: Dictionary of mean values for those reference periods.
  - `trend`: Decadal trend.

## Credits

- [Predictia](https://predictia.es) - Predictia Intelligent Data Solutions S.L.
- [IFCA](https://ifca.unican.es/es-es) - Instituto de Física de Cantabria

## License

Copyright 2024, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## FAQ / Troubleshooting

### Why do integer indices (e.g., frost days) return float values?

Indices like "frost days" (fd) or "wet days" (r1mm) are counts of days, so you might expect integer values. However, the API returns data that is **spatially aggregated** over a region (e.g., a NUTS-3 region). The value returned is the average count across all grid points within that region, which results in a floating-point number (e.g., 52.8 days).
