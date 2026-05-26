"""
Financial Metrics Tool — Fetches fundamental data for Indian stocks.

Uses yfinance to extract PE, EPS, revenue growth, profit margins,
debt-to-equity, ROE, dividend yield, and market cap.
"""

import json
from typing import Type

import yfinance as yf
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class FinancialMetricsInput(BaseModel):
    """Input schema for FinancialMetricsTool."""

    symbol: str = Field(
        ...,
        description="Indian stock symbol with exchange suffix, e.g. 'RELIANCE.NS'.",
    )


class FinancialMetricsTool(BaseTool):
    name: str = "financial_metrics_fetcher"
    description: str = (
        "Fetches fundamental financial metrics for a stock including PE ratio, EPS, "
        "revenue growth, profit margins, debt-to-equity, ROE, dividend yield, and market cap. "
        "Provide the stock symbol with .NS or .BO suffix."
    )
    args_schema: Type[BaseModel] = FinancialMetricsInput

    def _run(self, symbol: str) -> str:
        """Fetch fundamental financial data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return json.dumps({"error": f"No fundamental data found for {symbol}"})

            # Extract fundamental metrics
            fundamentals = {
                "symbol": symbol,
                "company_name": info.get("longName", info.get("shortName", "N/A")),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),

                # Valuation
                "market_cap": info.get("marketCap", "N/A"),
                "enterprise_value": info.get("enterpriseValue", "N/A"),
                "trailing_pe": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "peg_ratio": info.get("pegRatio", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),

                # Profitability
                "eps_trailing": info.get("trailingEps", "N/A"),
                "eps_forward": info.get("forwardEps", "N/A"),
                "profit_margin": info.get("profitMargins", "N/A"),
                "operating_margin": info.get("operatingMargins", "N/A"),
                "gross_margin": info.get("grossMargins", "N/A"),

                # Growth
                "revenue_growth": info.get("revenueGrowth", "N/A"),
                "earnings_growth": info.get("earningsGrowth", "N/A"),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth", "N/A"),

                # Financial Health
                "total_debt": info.get("totalDebt", "N/A"),
                "total_cash": info.get("totalCash", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "current_ratio": info.get("currentRatio", "N/A"),

                # Returns
                "return_on_equity": info.get("returnOnEquity", "N/A"),
                "return_on_assets": info.get("returnOnAssets", "N/A"),

                # Dividends
                "dividend_yield": info.get("dividendYield", "N/A"),
                "dividend_rate": info.get("dividendRate", "N/A"),
                "payout_ratio": info.get("payoutRatio", "N/A"),
                "ex_dividend_date": info.get("exDividendDate", "N/A"),

                # Revenue
                "total_revenue": info.get("totalRevenue", "N/A"),
                "revenue_per_share": info.get("revenuePerShare", "N/A"),

                # Analyst Data
                "target_mean_price": info.get("targetMeanPrice", "N/A"),
                "recommendation_key": info.get("recommendationKey", "N/A"),
                "number_of_analyst_opinions": info.get("numberOfAnalystOpinions", "N/A"),
            }

            return json.dumps(fundamentals, indent=2, default=str)

        except Exception as e:
            return json.dumps(
                {"error": f"Failed to fetch financial metrics for {symbol}: {str(e)}"}
            )
