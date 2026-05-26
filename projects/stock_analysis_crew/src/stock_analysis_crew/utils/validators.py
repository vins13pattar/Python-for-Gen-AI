"""
Validators — Stock symbol validation utilities.
"""

import re

import yfinance as yf


def validate_symbol(symbol: str) -> tuple[bool, str]:
    """
    Validate an Indian stock symbol.

    Args:
        symbol: Stock symbol string (e.g., 'RELIANCE.NS')

    Returns:
        Tuple of (is_valid, message).
        If valid: (True, "Symbol is valid.")
        If invalid: (False, "Error description.")
    """
    # Check empty
    if not symbol or not symbol.strip():
        return False, "Stock symbol cannot be empty."

    symbol = symbol.strip().upper()

    # Check format — must end with .NS or .BO
    if not re.match(r"^[A-Z0-9&_-]+\.(NS|BO)$", symbol):
        return (
            False,
            f"Invalid symbol format: '{symbol}'. "
            "Indian stock symbols must end with .NS (NSE) or .BO (BSE). "
            "Example: RELIANCE.NS, TCS.NS, INFY.BO",
        )

    # Verify data availability via yfinance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Check if we got meaningful data
        if not info or info.get("regularMarketPrice") is None:
            # Try fetching history as a secondary check
            hist = ticker.history(period="5d")
            if hist.empty:
                return (
                    False,
                    f"No market data found for '{symbol}'. "
                    "Please verify the stock symbol is correct.",
                )

        return True, f"Symbol '{symbol}' is valid."

    except Exception as e:
        return (
            False,
            f"Unable to validate '{symbol}': {str(e)}. "
            "Please check your internet connection and try again.",
        )
