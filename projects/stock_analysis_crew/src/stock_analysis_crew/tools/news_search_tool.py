"""
News Search Tool — Searches for recent stock news headlines.

Wraps a simple web search query focused on Indian stock market news.
The News Sentiment Agent uses this to gather recent headlines for sentiment analysis.
"""

import json
from typing import Type

import yfinance as yf
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class NewsSearchInput(BaseModel):
    """Input schema for NewsSearchTool."""

    symbol: str = Field(
        ...,
        description="Indian stock symbol, e.g. 'RELIANCE.NS'. The tool will extract the company name for searching.",
    )


class NewsSearchTool(BaseTool):
    name: str = "stock_news_searcher"
    description: str = (
        "Searches for recent news headlines about an Indian stock. "
        "Provide the stock symbol (e.g. RELIANCE.NS) and the tool will "
        "find the company name and search for recent news. "
        "Returns recent news items with titles and links."
    )
    args_schema: Type[BaseModel] = NewsSearchInput

    def _run(self, symbol: str) -> str:
        """Fetch recent news for a stock using yfinance news API."""
        try:
            ticker = yf.Ticker(symbol)

            # Get company name for context
            info = ticker.info
            company_name = info.get("longName", info.get("shortName", symbol.split(".")[0]))

            # Use yfinance's built-in news
            news_items = ticker.news

            if not news_items:
                return json.dumps({
                    "symbol": symbol,
                    "company_name": company_name,
                    "news_count": 0,
                    "news": [],
                    "note": "No recent news found via yfinance. The News Sentiment Agent should use the Serper web search tool for more comprehensive results."
                })

            # Process news items
            processed_news = []
            for item in news_items[:10]:  # Limit to 10 most recent
                content = item.get("content", {})
                news_entry = {
                    "title": content.get("title", item.get("title", "N/A")),
                    "publisher": content.get("provider", {}).get("displayName", "N/A"),
                    "link": content.get("canonicalUrl", {}).get("url", item.get("link", "N/A")),
                    "published": content.get("pubDate", "N/A"),
                }
                processed_news.append(news_entry)

            result = {
                "symbol": symbol,
                "company_name": company_name,
                "news_count": len(processed_news),
                "news": processed_news,
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to fetch news for {symbol}: {str(e)}",
                "fallback": f"Search the web for '{symbol.split('.')[0]} stock news India latest' using the Serper search tool."
            })
