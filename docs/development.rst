Development
===========

This section contains information for developers working on the OSCARS RSOTC Backend.

Local Setup
-----------

1. Clone the repository.
2. Create the conda environment:

   .. code-block:: bash

      conda env create -f environment.yml

3. Activate the environment:

   .. code-block:: bash

      conda activate oscars-rsotc-backend

4. Run the development server:

   .. code-block:: bash

      python main.py

Data Processing Utilities
-------------------------

The backend includes utilities to handle specific data type issues found in climate datasets.

* **ensure_data_type**: Located in `app.utils.ensure_data_type`. This module provides the `ensure_float` function, which is critical for converting `timedelta64` values (common in indices like frost days) into float days before serialization. This prevents issues where such values are serialized as nanoseconds (integers) by default.
