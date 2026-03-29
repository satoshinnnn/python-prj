from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import annual_to_daily_rf, RF_ANNUAL_DEFAULT


METRIC_INDEX = ["Mean Return", "Sigma", "Sharpe", "VaR (95%)", "Max Drawdown", "Beta (ETH)"]


def compute_drawdown(returns: pd.Series) -> pd.Series:
    cumulative = (1 + returns.fillna(0)).cumprod()
    running_peak = cumulative.cummax()
    drawdown = (cumulative - running_peak) / running_peak
    return drawdown


def compute_asset_metrics(returns: pd.Series, rf_daily: float) -> dict:
    clean = returns.dropna()
    mean_ret = clean.mean()
    sigma = clean.std(ddof=1)
    sharpe = np.nan if sigma == 0 or np.isnan(sigma) else (mean_ret - rf_daily) / sigma
    var_95 = clean.quantile(0.05)
    mdd = compute_drawdown(clean).min()
    return {
        "Mean Return": mean_ret,
        "Sigma": sigma,
        "Sharpe": sharpe,
        "VaR (95%)": var_95,
        "Max Drawdown": mdd,
    }


def compute_beta(eth_returns: pd.Series, btc_returns: pd.Series) -> float:
    aligned = pd.concat([eth_returns, btc_returns], axis=1).dropna()
    aligned.columns = ["eth", "btc"]
    if aligned["btc"].var(ddof=1) == 0:
        return np.nan
    return aligned["eth"].cov(aligned["btc"]) / aligned["btc"].var(ddof=1)


def build_summary_table(merged_df: pd.DataFrame, rf_annual: float = RF_ANNUAL_DEFAULT) -> pd.DataFrame:
    rf_daily = annual_to_daily_rf(rf_annual)

    btc_metrics = compute_asset_metrics(merged_df["btc_ret"], rf_daily)
    eth_metrics = compute_asset_metrics(merged_df["eth_ret"], rf_daily)
    beta_eth = compute_beta(merged_df["eth_ret"], merged_df["btc_ret"])

    summary = pd.DataFrame(index=METRIC_INDEX, columns=["BTC", "ETH"], dtype=float)
    for key in ["Mean Return", "Sigma", "Sharpe", "VaR (95%)", "Max Drawdown"]:
        summary.loc[key, "BTC"] = btc_metrics[key]
        summary.loc[key, "ETH"] = eth_metrics[key]

    summary.loc["Beta (ETH)", "BTC"] = 1.0
    summary.loc["Beta (ETH)", "ETH"] = beta_eth
    return summary


def add_rolling_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    out = df.copy()
    out["btc_vol"] = out["btc_ret"].rolling(window).std()
    out["eth_vol"] = out["eth_ret"].rolling(window).std()
    return out


def add_drawdowns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["btc_drawdown"] = compute_drawdown(out["btc_ret"])
    out["eth_drawdown"] = compute_drawdown(out["eth_ret"])
    return out



