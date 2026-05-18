# Scripts

This folder contains helper scripts for preparing and exporting station data.

build_ionospheric_stations_excel.py
- Generates `output/ionospheric_stations_world.xlsx` from
  `backend/app/data/stations.json`.
- Requirements: Python 3.8+ and `openpyxl`.

Run:
```bash
pip install openpyxl
python scripts/build_ionospheric_stations_excel.py
```

The script will write `output/ionospheric_stations_world.xlsx` and a
`Источники` sheet that summarizes `source` values.

Notes:
- The script will not invent missing data; it writes "нет данных" when
  a field is missing.
- Duplicates are removed by URSI code (`id` field in the JSON).
