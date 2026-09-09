"""
Tier-2 feasibility screen for the B1-C crime corpus (CourtListener API).

Counts candidate federal criminal dockets with TRIAL dispositions (not
pleas), by outcome type, to verify the 100-300 case target is realistic
before building the dossier pipeline. Read-only, keyless (rate-limited);
set COURTLISTENER_TOKEN for higher limits.

Usage:
    python build_tier2_screen.py            # counts only
    python build_tier2_screen.py --sample 5 # also print 5 example dockets
"""
from __future__ import annotations
import argparse, json, os, time, urllib.parse, urllib.request

BASE = "https://www.courtlistener.com/api/rest/v4/search/"

QUERIES = {
    # RECAP docket search (type=r); nature-of-suit filtering is civil-only,
    # so criminal screening rides on query terms + court + date range.
    "jury acquittal":  'caseName:("USA v." OR "United States v.") AND "judgment of acquittal"',
    "jury verdict":    'caseName:("USA v." OR "United States v.") AND "jury verdict"',
    "hung jury":       'caseName:("USA v." OR "United States v.") AND "mistrial"',
    "vacated":         'caseName:("USA v." OR "United States v.") AND "conviction vacated"',
}

def hit_count(q: str, filed_after="2015-01-01") -> int:
    params = {"type": "r", "q": q, "filed_after": filed_after, "order_by": "score desc"}
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "gist-eval-research"})
    tok = os.environ.get("COURTLISTENER_TOKEN")
    if tok:
        req.add_header("Authorization", f"Token {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("count", -1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    total = 0
    for label, q in QUERIES.items():
        try:
            n = hit_count(q)
        except Exception as e:
            n = -1
            print(f"{label:16} ERROR {str(e)[:80]}")
        else:
            print(f"{label:16} {n:>8,} dockets since 2015")
            total += max(n, 0)
        time.sleep(1.5)  # keyless rate courtesy
    print(f"\ncrude upper bound (overlapping): {total:,}")
    print("Next step if counts >> 300: add outcome parsing from docket "
          "entries + district stratification in the dossier builder.")

if __name__ == "__main__":
    main()
