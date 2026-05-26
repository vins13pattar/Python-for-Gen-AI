"""
Stock Price Tool — Fetches current market data for Indian stocks using yfinance.

Usage by Market Data Agent to retrieve price, volume, and basic market info.
"""

import json
from typing import Type

import yfinance as yf
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class StockPriceInput(BaseModel):
    """Input schema for StockPriceTool."""

    symbol: str = Field(
        ...,
        description="Indian stock symbol with exchange suffix, e.g. 'RELIANCE.NS' for NSE or 'RELIANCE.BO' for BSE.",
    )


class StockPriceTool(BaseTool):
    name: str = "stock_price_fetcher"
    description: str = (
        "Fetches current/latest available market data for an Indian stock. "
        "Provide the stock symbol with .NS (NSE) or .BO (BSE) suffix. "
        "Returns price, volume, market cap, PE ratio, 52-week range, and more."
    )
    args_schema: Type[BaseModel] = StockPriceInput

    def _run(self, symbol: str) -> str:
        """Fetch stock price data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get("regularMarketPrice") is None:
                # Try fast_info as fallback
                fast = ticker.fast_info
                if not fast:
                    return json.dumps({"error": f"No data found for symbol: {symbol}"})

            # Extract market data
            market_data = {
                "symbol": symbol,
                "company_name": info.get("longName", info.get("shortName", "N/A")),
                "current_price": info.get("regularMarketPrice")
                or info.get("currentPrice", "N/A"),
                "previous_close": info.get("regularMarketPreviousClose")
                or info.get("previousClose", "N/A"),
                "open": info.get("regularMarketOpen") or info.get("open", "N/A"),
                "day_high": info.get("regularMarketDayHigh")
                or info.get("dayHigh", "N/A"),
                "day_low": info.get("regularMarketDayLow")
                or info.get("dayLow", "N/A"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "volume": info.get("regularMarketVolume") or info.get("volume", "N/A"),
                "average_volume": info.get("averageVolume", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "beta": info.get("beta", "N/A"),
                "currency": info.get("currency", "INR"),
                "exchange": info.get("exchange", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
            }

            return json.dumps(market_data, indent=2, default=str)

        except Exception as e:
            return json.dumps(
                {"error": f"Failed to fetch data for {symbol}: {str(e)}"}
            )
