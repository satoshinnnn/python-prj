from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import requests

from .utils import BINANCE_BASE_URL


def _to_millis(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _fetch_klines_page(
    session: requests.Session,
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
    limit: int = 1000,
) -> list:
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": limit,
    }
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected Binance response for {symbol}: {payload}")
    return payload

from dateutil.relativedelta import relativedelta

def fetch_historical_daily_data(
    symbol: str,
    years: int,
    interval: str = "1d",
    out_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Fetch daily historical klines from Binance and optionally store time/close to CSV."""
    if years <= 0:
        raise ValueError("years must be > 0")

    # Use calendar years instead of 365 * years
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - relativedelta(years=years)

    start_ms = _to_millis(start_dt)
    end_ms = _to_millis(end_dt)

    session = requests.Session()
    rows: List[Tuple[int, float]] = []
    next_start = start_ms
    last_open_time = None

    while True:
        page = _fetch_klines_page(session, symbol, interval, next_start, end_ms, limit=1000)
        if not page:
            break

        for row in page:
            open_time = int(row[0])
            close_price = float(row[4])
            rows.append((open_time, close_price))
            last_open_time = open_time

        if len(page) < 1000:
            break

        next_start = last_open_time + 1
        if next_start >= end_ms:
            break

    df = pd.DataFrame(rows, columns=["time", "close"])
    df = df.drop_duplicates(subset=["time"]).sort_values("time").reset_index(drop=True)

    # Keep UTC internally, then write out as naive UTC time for CSV consistency
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True).dt.tz_convert(None)
    df["close"] = df["close"].astype(float)

    if out_csv is not None:
        out_path = Path(out_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)

    return df

def load_price_csv(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    df["close"] = df["close"].astype(float)
    df = df.sort_values("time").reset_index(drop=True)
    return df


def prepare_asset_frame(df: pd.DataFrame, asset_name: str) -> pd.DataFrame:
    out = df.copy()
    out["ret"] = out["close"].pct_change()
    out = out[["time", "close", "ret"]].rename(columns={"close": f"{asset_name}_close", "ret": f"{asset_name}_ret"})
    return out


def merge_assets(btc_df: pd.DataFrame, eth_df: pd.DataFrame) -> pd.DataFrame:
    btc = prepare_asset_frame(btc_df, "btc")
    eth = prepare_asset_frame(eth_df, "eth")
    merged = pd.merge(btc, eth, on="time", how="inner")
    merged = merged.dropna(subset=["btc_ret", "eth_ret"]).reset_index(drop=True)
    return merged
