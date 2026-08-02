#!/usr/bin/env python3
"""Download the longest Yahoo Finance daily price-index history for ^GSPC and ^NDX.

The saved series are price indices, not total-return indices.  The CSV is a
source-level cache: it preserves the daily OHLCV values returned by Yahoo and
records when it was retrieved so later research remains reproducible.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


USER_AGENT = "usa-stocks-info research contact@example.com"
SOURCE = "Yahoo Finance chart API; interval=1d; price index daily OHLCV"
INDEXES = {
    "^GSPC": {"name": "S&P 500", "requested_start": date(1928, 1, 3)},
    "^NDX": {"name": "Nasdaq-100", "requested_start": date(1985, 1, 31)},
}
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def as_date(timestamp: int) -> date:
    """Convert Unix seconds without Windows' pre-1970 timestamp limitation."""
    return (EPOCH + timedelta(seconds=timestamp)).date()


def number(values: list[Any], position: int) -> float | str:
    value = values[position] if position < len(values) else None
    return round(float(value), 8) if value is not None else ""


def fetch_index(symbol: str, name: str, start: date, end: date) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    period1 = int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())
    query = urllib.parse.urlencode({"period1": period1, "period2": period2, "interval": "1d", "events": "history"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    result = payload.get("chart", {}).get("result") or []
    if not result:
        error = (payload.get("chart", {}).get("error") or {}).get("description", "empty chart result")
        raise RuntimeError(error)

    chart = result[0]
    timestamps = chart.get("timestamp") or []
    quote = ((chart.get("indicators") or {}).get("quote") or [{}])[0]
    adjusted = ((chart.get("indicators") or {}).get("adjclose") or [{}])[0].get("adjclose") or []
    retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rows = []
    for position, timestamp in enumerate(timestamps):
        price_date = as_date(int(timestamp))
        close = number(quote.get("close") or [], position)
        if not close or not (start <= price_date <= end):
            continue
        rows.append(
            {
                "index_symbol": symbol,
                "index_name": name,
                "date": price_date.isoformat(),
                "open": number(quote.get("open") or [], position),
                "high": number(quote.get("high") or [], position),
                "low": number(quote.get("low") or [], position),
                "close": close,
                "volume": number(quote.get("volume") or [], position),
                "adjusted_close": number(adjusted, position),
                "source": SOURCE,
                "retrieved_at_utc": retrieved_at,
            }
        )
    metadata = chart.get("meta") or {}
    return rows, {
        "symbol": symbol,
        "name": name,
        "requested_start": start.isoformat(),
        "returned_start": rows[0]["date"] if rows else None,
        "returned_end": rows[-1]["date"] if rows else None,
        "observations": len(rows),
        "yahoo_exchange_timezone": metadata.get("exchangeTimezoneName"),
        "yahoo_data_granularity": metadata.get("dataGranularity"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "index_symbol", "index_name", "date", "open", "high", "low", "close", "volume", "adjusted_close", "source", "retrieved_at_utc",
    ]
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/indices/us_price_indices_daily.csv"))
    parser.add_argument("--metadata", type=Path, default=Path("data/indices/us_price_indices_daily_metadata.json"))
    parser.add_argument("--end-date", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    series = []
    for symbol, details in INDEXES.items():
        index_rows, index_metadata = fetch_index(symbol, details["name"], details["requested_start"], args.end_date)
        rows.extend(index_rows)
        series.append(index_metadata)
        print(f"{symbol}: {index_metadata['observations']} rows, {index_metadata['returned_start']} to {index_metadata['returned_end']}", flush=True)

    rows.sort(key=lambda row: (row["index_symbol"], row["date"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, rows)
    args.metadata.write_text(
        json.dumps(
            {
                "dataset": "U.S. equity price indices daily history",
                "index_type": "Price return; excludes dividends",
                "source": SOURCE,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "series": series,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
