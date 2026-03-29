from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import add_drawdowns, add_rolling_volatility


def _style_axes(ax, title: str, xlabel: str, ylabel: str):
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)


def plot_risk_return(summary_df: pd.DataFrame, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(summary_df.loc["Sigma", "BTC"], summary_df.loc["Mean Return", "BTC"], s=120, color="gold", edgecolor="black", label="BTC")
    ax.scatter(summary_df.loc["Sigma", "ETH"], summary_df.loc["Mean Return", "ETH"], s=120, color="blue", edgecolor="black", label="ETH")
    ax.annotate("BTC", (summary_df.loc["Sigma", "BTC"], summary_df.loc["Mean Return", "BTC"]), xytext=(8, 8), textcoords="offset points")
    ax.annotate("ETH", (summary_df.loc["Sigma", "ETH"], summary_df.loc["Mean Return", "ETH"]), xytext=(8, 8), textcoords="offset points")
    _style_axes(ax, "Risk vs Return", "Volatility (Sigma)", "Mean Daily Return")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    # plt.show()
    # plt.close(fig)

def plot_rolling_volatility(merged_df: pd.DataFrame, output_path: str | Path, window: int = 30) -> None:
    df = add_rolling_volatility(merged_df, window=window)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["time"], df["btc_vol"], color="gold", linewidth=2, label=f"BTC {window}D Vol")
    ax.plot(df["time"], df["eth_vol"], color="blue", linewidth=2, label=f"ETH {window}D Vol")
    _style_axes(ax, f"Rolling Volatility ({window}-day window)", "Time", "Rolling Std of Daily Returns")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    # plt.show()
    # plt.close(fig)

def plot_return_distribution(merged_df: pd.DataFrame, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(merged_df["btc_ret"].dropna(), bins=60, alpha=0.5, density=True, color="gold", label="BTC")
    ax.hist(merged_df["eth_ret"].dropna(), bins=60, alpha=0.5, density=True, color="blue", label="ETH")
    _style_axes(ax, "Return Distribution", "Daily Return", "Density")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    # plt.show()
    # plt.close(fig)

def plot_drawdown(merged_df: pd.DataFrame, output_path: str | Path) -> None:
    df = add_drawdowns(merged_df)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["time"], df["btc_drawdown"] * 100, color="#f4e3a1", linewidth=2.2, label="BTC Drawdown")
    ax.plot(df["time"], df["eth_drawdown"] * 100, color="#8ecae6", linewidth=2.2, label="ETH Drawdown")
    _style_axes(ax, "Drawdown Comparison", "Time", "Drawdown (%)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    # plt.show()
    # plt.close(fig)

def plot_dashboard(summary_df, merged_df, output_path):
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # --- Chart 1: Risk vs Return ---
    ax = axs[0, 0]
    ax.scatter(summary_df.loc["Sigma", "BTC"], summary_df.loc["Mean Return", "BTC"],
               color="gold", s=100, label="BTC")
    ax.scatter(summary_df.loc["Sigma", "ETH"], summary_df.loc["Mean Return", "ETH"],
               color="blue", s=100, label="ETH")
    ax.set_title("Risk vs Return")
    ax.set_xlabel("Sigma")
    ax.set_ylabel("Return")
    ax.legend()

    # --- Chart 2: Rolling Vol ---
    from .metrics import add_rolling_volatility
    df_vol = add_rolling_volatility(merged_df)

    ax = axs[0, 1]
    ax.plot(df_vol["time"], df_vol["btc_vol"], color="gold", label="BTC")
    ax.plot(df_vol["time"], df_vol["eth_vol"], color="blue", label="ETH")
    ax.set_title("Rolling Volatility")
    ax.legend()

    # --- Chart 3: Distribution ---
    ax = axs[1, 0]
    ax.hist(merged_df["btc_ret"].dropna(), bins=50, alpha=0.5, color="gold", label="BTC")
    ax.hist(merged_df["eth_ret"].dropna(), bins=50, alpha=0.5, color="blue", label="ETH")
    ax.set_title("Return Distribution")
    ax.legend()

    # --- Chart 4: Drawdown ---
    from .metrics import add_drawdowns
    df_dd = add_drawdowns(merged_df)

    ax = axs[1, 1]
    ax.plot(df_dd["time"], df_dd["btc_drawdown"] * 100, color="#f4e3a1", label="BTC")
    ax.plot(df_dd["time"], df_dd["eth_drawdown"] * 100, color="#8ecae6", label="ETH")
    ax.set_title("Drawdown")
    ax.legend()

    plt.tight_layout()

    fig.savefig(output_path, dpi=200)

    plt.show()      # 👁️ hiện 1 lần
    plt.close(fig)  # 🧹 giải phóng RAM



