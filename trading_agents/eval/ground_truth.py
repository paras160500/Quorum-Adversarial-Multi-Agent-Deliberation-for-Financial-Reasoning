"""
Objective backtest-style evaluation: did the signal actually make money?
Originally notebook cell 8.2.1.
"""
from datetime import datetime, timedelta

import yfinance as yf


def evaluate_ground_truth(ticker: str, trade_date: str, signal: str) -> str:
    try:
        start_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        # Check data for the next 8 calendar days to increase chance of getting 5 trading days
        end_date = start_date + timedelta(days=8)

        data = yf.download(ticker, start=start_date.isoformat(), end=end_date.isoformat(), progress=False)
        if len(data) < 5:
            return f"Insufficient data for ground truth evaluation. Found only {len(data)} days."

        first_trading_day_index = 0
        while data.index[first_trading_day_index].date() < start_date:
            first_trading_day_index += 1
            if first_trading_day_index >= len(data) - 5:
                return "Could not align trade date."

        open_price = data["Open"].iloc[first_trading_day_index]
        close_price_5_days_later = data["Close"].iloc[first_trading_day_index + 4]
        performance = ((close_price_5_days_later - open_price) / open_price) * 100

        result = "INCORRECT DECISION"
        if (
            (signal == "BUY" and performance > 1)
            or (signal == "SELL" and performance < -1)
            or (signal == "HOLD" and -1 <= performance <= 1)
        ):
            result = "CORRECT DECISION"

        return (
            "----- Ground Truth Evaluation Report -----\n"
            f"Agent Signal: {signal} on {trade_date}\n"
            f"Opening Price on {data.index[first_trading_day_index].strftime('%Y-%m-%d')}: ${open_price:.2f}\n"
            f"Closing Price 5 days later ({data.index[first_trading_day_index + 4].strftime('%Y-%m-%d')}): "
            f"${close_price_5_days_later:.2f}\n"
            f"Actual Market Performance: {performance:+.2f}%\n"
            f"Evaluation Result: {result}"
        )
    except Exception as e:
        return f"Ground truth evaluation failed: {e}"
