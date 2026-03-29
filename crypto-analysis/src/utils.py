from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

RF_ANNUAL_DEFAULT = 0.025
TRADING_DAYS = 252
BINANCE_BASE_URL = "https://api.binance.com"


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data_dir: Path
    output_dir: Path
    btc_csv: Path
    eth_csv: Path
    metrics_csv: Path


def build_paths(root: Path) -> ProjectPaths:
    data_dir = root / "data"
    output_dir = root / "output"
    return ProjectPaths(
        root=root,
        data_dir=data_dir,
        output_dir=output_dir,
        btc_csv=data_dir / "btc.csv",
        eth_csv=data_dir / "eth.csv",
        metrics_csv=output_dir / "metrics_summary.csv",
    )


def ensure_directories(paths: ProjectPaths) -> None:
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.output_dir.mkdir(parents=True, exist_ok=True)


def annual_to_daily_rf(rf_annual: float = RF_ANNUAL_DEFAULT) -> float:
    return rf_annual / TRADING_DAYS


def pretty_metrics_table(df: pd.DataFrame) -> str:
    return df.to_string(float_format=lambda x: f"{x:.6f}")


def interpret_results(summary_df: pd.DataFrame) -> str:
    """Create a concise investment-style interpretation from computed metrics."""
    btc = summary_df["BTC"]
    eth = summary_df["ETH"]

    higher_return = "BTC" if btc["Mean Return"] > eth["Mean Return"] else "ETH"
    lower_vol = "BTC" if btc["Sigma"] < eth["Sigma"] else "ETH"
    better_sharpe = "BTC" if btc["Sharpe"] > eth["Sharpe"] else "ETH"
    worse_var = "BTC" if btc["VaR (95%)"] < eth["VaR (95%)"] else "ETH"
    worse_mdd = "BTC" if btc["Max Drawdown"] < eth["Max Drawdown"] else "ETH"

    lines = [
        f"• Higher average daily return: {higher_return}",
        f"• Lower volatility / more stable: {lower_vol}",
        f"• Better risk-adjusted return (Sharpe): {better_sharpe}",
        f"• Worse tail loss by VaR: {worse_var}",
        f"• Deeper max drawdown: {worse_mdd}",
        (
            f"• ETH beta vs BTC: {summary_df.loc['Beta (ETH)', 'ETH']:.4f} "
            f"(beta measures ETH's sensitivity relative to BTC)"
        ),
    ]
    return "\n".join(lines)
