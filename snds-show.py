#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import os
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def open_maybe_gz(path: Path, mode: str = "rt"):
    # mode: "rt" for text, "rb" for bytes
    if path.suffix == ".gz":
        return gzip.open(path, mode, encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")


def find_file(data_dir: Path, prefix: str, tag: str) -> Optional[Path]:
    """
    Finds either .csv or .csv.gz for a given prefix/tag.
    Example: prefix="snds-data", tag="2025-11-01"
    """
    candidates = [
        data_dir / f"{prefix}-{tag}.csv",
        data_dir / f"{prefix}-{tag}.csv.gz",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with open_maybe_gz(path, "rt") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        rows = [row for row in reader]
    return rows


def read_csv_rows(path: Path) -> List[List[str]]:
    with open_maybe_gz(path, "rt") as f:
        reader = csv.reader(f)
        rows = [r for r in reader]
    return rows


def tabulate(rows: List[Dict[str, str]], columns: List[str], limit: int) -> str:
    # Build table with fixed-width columns.
    selected = rows[:limit] if limit > 0 else rows
    widths = []
    for col in columns:
        max_len = len(col)
        for r in selected:
            max_len = max(max_len, len(str(r.get(col, ""))))
        widths.append(max_len)

    def fmt_row(values: List[str]) -> str:
        parts = []
        for i, v in enumerate(values):
            parts.append(str(v).ljust(widths[i]))
        return "  ".join(parts)

    header = fmt_row(columns)
    sep = fmt_row(["-" * w for w in widths])

    lines = [header, sep]
    for r in selected:
        lines.append(fmt_row([r.get(c, "") for c in columns]))
    return "\n".join(lines)


def guess_columns(rows: List[Dict[str, str]], wanted: List[str]) -> List[str]:
    if not rows:
        return []
    available = list(rows[0].keys())
    # Pick columns that exist (case-sensitive first), otherwise try case-insensitive match.
    result: List[str] = []
    lower_map = {a.lower(): a for a in available}
    for w in wanted:
        if w in available:
            result.append(w)
        else:
            a = lower_map.get(w.lower())
            if a:
                result.append(a)
    # Fallback: if none found, show first few columns.
    if not result:
        result = available[:8]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show Microsoft SNDS CSV exports in a readable CLI table."
    )
    parser.add_argument(
        "--dir",
        default=str(Path(__file__).resolve().parent / "data"),
        help="Data directory (default: ./data next to this script).",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date tag used in filenames, format YYYY-MM-DD (e.g. 2025-11-01). "
             "Default: today.",
    )
    parser.add_argument(
        "--type",
        choices=["data", "ipstatus", "both"],
        default="both",
        help="Which SNDS file to show.",
    )
    parser.add_argument(
        "--columns",
        default=None,
        help="Comma-separated list of columns to display (for 'data' only).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Max rows to display (0 = no limit). Default: 30.",
    )

    args = parser.parse_args()

    data_dir = Path(args.dir).expanduser().resolve()
    if not data_dir.exists():
        eprint(f"ERROR: Data directory not found: {data_dir}")
        return 2

    tag = args.date or date.today().isoformat()

    if args.type in ("data", "both"):
        path = find_file(data_dir, "snds-data", tag)
        if not path:
            eprint(f"ERROR: Could not find snds-data-{tag}.csv(.gz) in {data_dir}")
        else:
            rows = read_csv_dicts(path)
            print(f"\n=== DATA: {path.name} ({len(rows)} rows) ===")
            if not rows:
                print("(No rows)")
            else:
                if args.columns:
                    cols = [c.strip() for c in args.columns.split(",") if c.strip()]
                else:
                    # Common-ish SNDS fields vary; we try reasonable defaults and fall back.
                    cols = guess_columns(
                        rows,
                        wanted=[
                            "IP", "ip", "IPv4", "ipv4",
                            "Date", "date",
                            "Traffic", "traffic",
                            "ComplaintRate", "complaintRate", "complaints",
                            "FilterResult", "filterResult",
                            "SRD", "srd",
                        ],
                    )
                print(tabulate(rows, cols, args.limit))

    if args.type in ("ipstatus", "both"):
        path = find_file(data_dir, "snds-ipStatus", tag)
        if not path:
            eprint(f"ERROR: Could not find snds-ipStatus-{tag}.csv(.gz) in {data_dir}")
        else:
            raw = read_csv_rows(path)
            print(f"\n=== IPSTATUS: {path.name} ({max(0, len(raw) - 1)} rows) ===")
            if not raw:
                print("(Empty file)")
            else:
                # ipStatus is also CSV, but columns vary; show first columns as-is.
                header = raw[0]
                body = raw[1:]
                # Convert to dicts for tabulation
                dict_rows = []
                for r in body:
                    d = {}
                    for i, h in enumerate(header):
                        d[h] = r[i] if i < len(r) else ""
                    dict_rows.append(d)

                cols = header[:8]  # keep it readable
                print(tabulate(dict_rows, cols, args.limit))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

