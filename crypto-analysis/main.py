from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data import fetch_historical_daily_data, load_price_csv, merge_assets
from src.metrics import build_summary_table
from src.plots import plot_drawdown, plot_risk_return, plot_return_distribution, plot_rolling_volatility
from src.utils import build_paths, ensure_directories, interpret_results, pretty_metrics_table, RF_ANNUAL_DEFAULT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze and compare BTC and ETH risk/return using Binance data.")
    parser.add_argument("--years", type=int, default=1, help="Historical window in years")
    parser.add_argument("--rf-annual", type=float, default=RF_ANNUAL_DEFAULT, help="Annual risk-free rate (default: 0.025)")
    parser.add_argument("--root", type=str, default=str(Path(__file__).resolve().parent), help="Project root directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_paths(Path(args.root))
    ensure_directories(paths)

    print(f"Fetching {args.years}-year daily data from Binance...")
    btc_df = fetch_historical_daily_data("BTCUSDT", years=args.years, interval="1d", out_csv=paths.btc_csv)
    eth_df = fetch_historical_daily_data("ETHUSDT", years=args.years, interval="1d", out_csv=paths.eth_csv)

    # Load back from CSV to make the processing step explicit and reproducible.
    btc_loaded = load_price_csv(paths.btc_csv)
    eth_loaded = load_price_csv(paths.eth_csv)
    merged_df = merge_assets(btc_loaded, eth_loaded)

    summary_df = build_summary_table(merged_df, rf_annual=args.rf_annual)
    summary_df.to_csv(paths.metrics_csv)

    print("\nSummary table:")
    print(pretty_metrics_table(summary_df))

    print("\nInsights:")
    print(interpret_results(summary_df))

    from src.plots import plot_dashboard

    plot_dashboard(summary_df, merged_df, paths.output_dir / "dashboard.png")

    print(f"\nFiles saved to: {paths.data_dir} and {paths.output_dir}")


if __name__ == "__main__":
    main()


