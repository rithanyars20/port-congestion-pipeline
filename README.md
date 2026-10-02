# Port Congestion Pipeline 🚢

A data pipeline that downloads global shipping data, cleans it, checks it for
errors, and flags ports with unusually high or low ship arrivals compared to
their recent average. Runs automatically every week via GitHub Actions.


## Why
A sudden drop or spike in ship arrivals at a port can signal congestion, a
blockage, a strike, a storm, or a shift in trade. This project is a personal
exercise in building a small pipeline that catches that kind of signal
automatically, end to end: download → store → clean → check → calculate →
publish results.


## How it works
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
fso14, Brazil - Offshore Oil Terminal 22, 2026-07-20, 0, 0.25, unusual
port157, Bossaso, 2026-07-20, 0, 1.5, unusual
port2062, Nanaimo, 2026-07-20, 2, 0.5, unusual
port178, Bruges, 2026-07-20, 4, 3.25, normal

Bossaso's arrivals dropped to zero against a recent average of 1.5, a sharp
enough drop to flag. Nanaimo's rose well above its usual 0.5, also flagged.
Bruges stayed close to normal and wasn't flagged.

## Problems I hit

- **CSV parsing error on quoted commas.** Some port names contain commas,
  e.g. `"Jimenez, Ozamis"`. DuckDB's CSV auto-detection guessed the wrong
  quote character, shifting later columns and causing a type error. Fixed
  by explicitly setting `quote = '"'` and `sample_size = -1` (scan the
  whole file instead of a sample) when loading the CSV.
- **Data lag.** Despite being labeled a weekly update, PortWatch's own data
  currently lags well behind the present (confirmed by checking
  `max(day)` in the loaded data directly). The pipeline correctly reflects
  whatever PortWatch's most recent published data is; it doesn't assume
  anything newer exists.
- **In-progress weeks.** Early versions of the model included the current,
  not-yet-complete week, which could get wrongly flagged as "unusual" simply
  for having too little data so far. Fixed by excluding any week that hasn't
  fully ended yet.
- **GitHub push rejected for the workflow file.** My personal access token
  initially lacked the `workflow` permission scope, which GitHub requires
  specifically for uploading files under `.github/workflows/`. Fixed by
  regenerating the token with that scope included.

## Tools used

Python, DuckDB, dbt, Git, GitHub Actions. Data source: IMF PortWatch.

