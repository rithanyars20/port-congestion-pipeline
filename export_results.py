import duckdb

con = duckdb.connect("port.duckdb")
con.execute("""
    copy (select * from weekly_port_arrivals order by week_start desc)
    to 'outputs/weekly_port_arrivals.csv' (header, delimiter ',')
""")
print("exported outputs/weekly_port_arrivals.csv")
