import glob, duckdb

latest = sorted(glob.glob("raw/ports_*.csv"))[-1]
con = duckdb.connect("port.duckdb")
con.execute(f"""
    create or replace table raw_ports as
    select * from read_csv(
        '{latest}',
        quote = '"',
        sample_size = -1
    )
""")
print("rows loaded:", con.execute("select count(*) from raw_ports").fetchone()[0])
