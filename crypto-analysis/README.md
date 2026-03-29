# Crypto Analysis: BTC vs ETH

A small Python project to compare the risk and return profile of BTC and ETH using historical daily candlestick data from the Binance public Spot API.

## What it does

- Downloads historical daily klines for `BTCUSDT` and `ETHUSDT`
- Saves clean CSV files in `data/`
- Computes:
  - mean daily return
  - volatility (sigma)
  - Sharpe ratio
  - Value at Risk at 95%
  - Max Drawdown
  - Beta of ETH relative to BTC
- Generates four charts in `output/`
- Prints a readable metrics table and interpretation

## Folder structure

```text
crypto-analysis/
├── data/
├── output/
├── src/
│   ├── data.py
│   ├── metrics.py
│   ├── plots.py
│   └── utils.py
├── main.py
├── requirements.txt
└── README.md
```

## Binance API source

The downloader uses Binance Spot public market data endpoint `GET /api/v3/klines`, which supports `symbol`, `interval`, `startTime`, `endTime`, and `limit`. Daily interval `1d` is supported, and the endpoint is public market data. citeturn368022search0turn368022search9

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py --years 5
```

Available timeframes:

```bash
python main.py --years 1
python main.py --years 2
python main.py --years 3
python main.py --years 4
python main.py --years 5
python main.py --years 6
python main.py --years 10
```

Optional custom risk-free rate:

```bash
python main.py --years 5 --rf-annual 0.025
```

## Methodology

### Daily return

```python
ret = pct_change(close)
```

### Volatility

```python
sigma = std(returns)
```

### Sharpe ratio

```python
sharpe = (mean_return - rf_daily) / sigma
```

### Value at Risk (95%)

5th percentile of daily returns.

### Max Drawdown

```python
cumulative = (1 + returns).cumprod()
running_peak = cumulative.cummax()
drawdown = (cumulative - running_peak) / running_peak
mdd = drawdown.min()
```

### Beta of ETH vs BTC

```python
beta = cov(ETH, BTC) / var(BTC)
```

## Outputs

- `data/btc.csv`
- `data/eth.csv`
- `output/metrics_summary.csv`
- `output/chart1_risk_return.png`
- `output/chart2_rolling_volatility.png`
- `output/chart3_return_distribution.png`
- `output/chart4_drawdown.png`

## Notes

- The code paginates requests automatically because Binance klines responses are limited per request.
- The project uses daily close prices only, as requested.
- The interpretation text is generated from the computed metrics, so it will adapt to any selected timeframe.
