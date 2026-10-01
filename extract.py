import datetime, pathlib, time, requests

URL = "https://portwatch.imf.org/datasets/83b1bbc7b3354c5fb1f40673bb8f852e/about"

def main():
    pathlib.Path("raw").mkdir(exist_ok=True)
    out = pathlib.Path("raw") / f"ports_{datetime.date.today()}.csv"
    for attempt in range(1, 4):
        try:
            r = requests.get(URL, timeout=120)
            r.raise_for_status()
            out.write_bytes(r.content)
            print("saved", out)
            return
        except requests.RequestException as e:
            print(f"attempt {attempt} failed: {e}")
            time.sleep(10)
    raise SystemExit("download failed after 3 tries")

main()
