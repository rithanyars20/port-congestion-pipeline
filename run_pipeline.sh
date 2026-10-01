#!/usr/bin/env bash
set -e
source .venv/bin/activate
python extract.py
python load.py
cd port_dbt
dbt run  --profiles-dir .
dbt test --profiles-dir .
