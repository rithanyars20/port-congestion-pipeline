# Port Congestion Pipeline
A data pipeline that downloads global shipping data, cleans it, checks it for
errors, and flags ports with unusually high or low ship arrivals compared to
their recent average. Runs automatically every week via GitHub Actions.


# Why
A sudden drop or spike in ship arrivals at a port can signal congestion, a
blockage, a strike, a storm, or a shift in trade. This project is a personal
exercise in building a small pipeline that catches that kind of signal
automatically, end to end: download → store → clean → check → calculate →
publish results.


# How it works
1. **Extract** (`extract.py`) — downloads the latest "Daily Port Activity
   Data" CSV from [IMF PortWatch](https://portwatch.imf.org), which tracks
   ~2,065 ports worldwide using AIS satellite ship-tracking data. Retries up
   to 3 times on failure.
2. **Load** (`load.py`) — loads the CSV into a local DuckDB database
   (`port.duckdb`) as a table called `raw_ports`. Rebuilds the table fresh
   each run, since each new file already contains the full history.
3. **Transform** (dbt models in `port_dbt/models/`):
   - `stg_ports.sql` — renames columns to clean names, fills missing ship
     counts with 0, drops rows with no port ID.
   - `weekly_port_arrivals.sql` — groups daily data into weekly totals per
     port, compares each week to the average of the previous 4 weeks, flags
     weeks where actual arrivals are below 60% or above 140% of that expected
     value, and excludes the current, still-in-progress week so it isn't
     falsely flagged on partial data.
4. **Test** (dbt tests) — 5 automatic checks: no null port IDs, no null
   dates, no null ship counts, no negative ship counts, no duplicate
   port+date rows. All currently pass.
5. **Export** (`export_results.py`) — saves the final flagged table to
   `outputs/weekly_port_arrivals.csv`, so results are viewable directly on
   GitHub without needing DuckDB installed.
6. **Schedule** (`.github/workflows/pipeline.yml`) — runs the entire pipeline
   automatically every Tuesday via GitHub Actions (shortly after PortWatch's
   own weekly update), and commits the refreshed results CSV back to this
   repo. Can also be triggered manually from the **Actions** tab.

## How to run it locally

```bash
git clone https://github.com/rithanyars20/port-congestion-pipeline.git
cd port-congestion-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_pipeline.sh
```

## Sample output

From `outputs/weekly_port_arrivals.csv`
(`port_id, port_name, week_start, actual_calls, expected_calls, flag`):
