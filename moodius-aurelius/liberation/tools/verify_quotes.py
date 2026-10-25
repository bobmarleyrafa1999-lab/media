#!/usr/bin/env python3
"""Check every public-domain quote in quotes.csv word for word against the Standard Ebooks source on GitHub.

Standard Ebooks texts are public domain and their editions are CC0, and raw.githubusercontent.com is
reachable from the project container, so this runs anywhere.

  python3 tools/verify_quotes.py            # exit code 1 if any checked quote is not found
"""
import csv
import os
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/standardebooks/{repo}/master/src/epub/text/{file}"
HERE = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\d+(?=[\s,.;:])", "", s)  # endnote numbers glued to words ("will11")
    s = s.replace("⁠", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    path = os.path.join(HERE, "..", "quotes.csv")
    cache, bad = {}, 0
    for row in csv.DictReader(open(path, encoding="utf-8")):
        if not row["check_repo"]:
            continue
        key = (row["check_repo"], row["check_file"])
        if key not in cache:
            url = RAW.format(repo=key[0], file=key[1])
            with urllib.request.urlopen(url, timeout=30) as r:
                cache[key] = norm(r.read().decode("utf-8"))
        ok = norm(row["quote"]) in cache[key]
        bad += not ok
        print(f"{'ok ' if ok else 'MISSING'} {row['id']} {row['author']}: {row['work']} {row['section']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
