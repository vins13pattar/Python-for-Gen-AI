"""
Technical Indicator Tool — Calculates SMA, RSI, MACD and other indicators.

Uses yfinance for historical data and pandas-ta for indicator calculations.
"""

import json
from typing import Type

import pandas as pd
import yfinance as yf

from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class TechnicalIndicatorInput(BaseModel):
    """Input schema for TechnicalIndicatorTool."""

    symbol: str = Field(
        ...,
        description="Indian stock symbol with exchange suffix, e.g. 'RELIANCE.NS'.",
    )
    period: str = Field(
        default="1y",
        description="Historical data period. Options: 1mo, 3mo, 6mo, 1y, 2y. Default: 1y.",
    )


class TechnicalIndicatorTool(BaseTool):
    name: str = "technical_indicator_calculator"
    description: str = (
        "Calculates technical indicators for a stock including SMA (20, 50, 200), "
        "RSI (14), MACD, volume trend, and identifies support/resistance levels. "
        "Provide the stock symbol with .NS or .BO suffix."
    )
    args_schema: Type[BaseModel] = TechnicalIndicatorInput

    def _run(self, symbol: str, period: str = "1y") -> str:
        """Calculate technical indicators using historical data."""
        try:
            import pandas_ta as ta

            # Fetch historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                return json.dumps(
                    {"error": f"No historical data found for {symbol} with period {period}"}
                )

            close = hist["Close"]
            volume = hist["Volume"]
            current_price = float(close.iloc[-1])

            # === SMA Calculations ===
            sma_20 = float(close.rolling(window=20).mean().iloc[-1]) if len(close) >= 20 else None
            sma_50 = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else None
            sma_200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else None

            # === RSI ===
            rsi_series = ta.rsi(close, length=14)
            rsi_value = float(rsi_series.iloc[-1]) if rsi_series is not None and not rsi_series.empty else None

            # === MACD ===
            macd_df = ta.macd(close, fast=12, slow=26, signal=9)
            macd_data = {}
            if macd_df is not None and not macd_df.empty:
                macd_cols = macd_df.columns
                macd_data = {
                    "macd_line": float(macd_df[macd_cols[0]].iloc[-1]),
                    "signal_line": float(macd_df[macd_cols[1]].iloc[-1]),
                    "histogram": float(macd_df[macd_cols[2]].iloc[-1]),
                }

            # === Volume Analysis ===
            avg_volume_20 = float(volume.rolling(window=20).mean().iloc[-1]) if len(volume) >= 20 else None
            current_volume = float(volume.iloc[-1])
            volume_trend = "N/A"
            if avg_volume_20:
                ratio = current_volume / avg_volume_20
                if ratio > 1.5:
                    volume_trend = "Significantly above average"
                elif ratio > 1.1:
                    volume_trend = "Above average"
                elif ratio > 0.9:
                    volume_trend = "Near average"
                else:
                    volume_trend = "Below average"

            # === Support / Resistance (simple: recent lows/highs) ===
            recent_data = hist.tail(60)
            support = float(recent_data["Low"].min())
            resistance = float(recent_data["High"].max())

            # === Trend Signals ===
            sma_signals = {}
            if sma_20:
                sma_signals["sma_20"] = round(sma_20, 2)
                sma_signals["price_vs_sma_20"] = "Above" if current_price > sma_20 else "Below"
            if sma_50:
                sma_signals["sma_50"] = round(sma_50, 2)
                sma_signals["price_vs_sma_50"] = "Above" if current_price > sma_50 else "Below"
            if sma_200:
                sma_signals["sma_200"] = round(sma_200, 2)
                sma_signals["price_vs_sma_200"] = "Above" if current_price > sma_200 else "Below"

            # === Overall Trend ===
            trend = "Neutral"
            if sma_50 and sma_200:
                if current_price > sma_50 > sma_200:
                    trend = "Strong Bullish"
                elif current_price > sma_50:
                    trend = "Bullish"
                elif current_price < sma_50 < sma_200:
                    trend = "Strong Bearish"
                elif current_price < sma_50:
                    trend = "Bearish"

            # === RSI Interpretation ===
            rsi_signal = "N/A"
            if rsi_value is not None:
                if rsi_value > 80:
                    rsi_signal = "Heavily Overbought"
                elif rsi_value > 70:
                    rsi_signal = "Overbought"
                elif rsi_value > 55:
                    rsi_signal = "Bullish"
                elif rsi_value > 45:
                    rsi_signal = "Neutral"
                elif rsi_value > 30:
                    rsi_signal = "Bearish"
                else:
                    rsi_signal = "Oversold"

            # === MACD Signal ===
            macd_signal = "N/A"
            if macd_data:
                if macd_data["histogram"] > 0:
                    macd_signal = "Positive momentum (bullish)"
                else:
                    macd_signal = "Negative momentum (bearish)"

            result = {
                "symbol": symbol,
                "period": period,
                "current_price": round(current_price, 2),
                "overall_trend": trend,
                "sma": sma_signals,
                "rsi": {
                    "value": round(rsi_value, 2) if rsi_value else None,
                    "signal": rsi_signal,
                },
                "macd": {
                    **macd_data,
                    "signal": macd_signal,
                },
                "volume": {
                    "current": int(current_volume),
                    "average_20d": int(avg_volume_20) if avg_volume_20 else None,
                    "trend": volume_trend,
                },
                "support_resistance": {
                    "support_60d": round(support, 2),
                    "resistance_60d": round(resistance, 2),
                },
                "data_points": len(close),
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps(
                {"error": f"Failed to calculate indicators for {symbol}: {str(e)}"}
            )
